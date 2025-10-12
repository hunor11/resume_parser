# resume_agent.py
from __future__ import annotations

import os
from operator import itemgetter

import psycopg
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector, PostgresChatMessageHistory


def _format_docs(docs: list[Document]) -> str:
    blocks = []
    for d in docs:
        src = d.metadata.get("source") or d.metadata.get("file") or "unknown"
        text = (d.page_content or "").strip()
        if text:
            blocks.append(f"[source: {src}]\n{text}")
    return "\n\n".join(blocks) if blocks else "NO_CONTEXT"


class ResumeAgent:
    """
    RAG chatbot for resume/job matching with conversation memory.
    - Retriever: PGVector (LangChain) on pgvector
    - Embeddings: all-MiniLM-L6-v2 (HuggingFace)
    - LLM: Gemini chat via langchain-google-genai
    - Memory: RunnableWithMessageHistory (per session_id)
    """

    def __init__(
        self,
        k: int = 5,
        session_id: str = "default",
    ) -> None:
        """
        Initialize the ResumeAgent.

        Args:
            - k: number of context documents to retrieve
            - session_id: identifier for chat session (memory)
        """
        load_dotenv()
        conn = os.environ["VECTOR_DB_URL"]
        if conn.startswith("postgres://"):  # aiven gives this URL format :(
            conn = conn.replace("postgres://", "postgresql+psycopg://", 1)

        embedding_model = (
            os.environ.get("EMBEDDING_MODEL") or "sentence-transformers/all-MiniLM-L6-v2"
        )
        collection_name = os.environ.get("RESUME_COLLECTION") or "resumes"
        self.emb = HuggingFaceEmbeddings(model_name=embedding_model)

        self.vs = PGVector(
            connection=conn,
            collection_name=collection_name,
            embeddings=self.emb,
        )
        self.k = k
        self.session_id = session_id

        kwargs = {"k": self.k or 5, "filter": {"session_id": {"$eq": session_id}}}
        self.retriever = self.vs.as_retriever(search_kwargs=kwargs)

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a recruitment assistant."
                        "Use ONLY the provided resume snippets.\n"
                        "- Cite like [source: <filename>] next to each claim.\n"
                        "- If context is insufficient, say so.\n"
                        "- Be concise and factual; do not invent details."
                    ),
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "User question:\n{question}\n\nContext:\n{context}"),
            ]
        )

        base_chain = (
            {
                "question": RunnablePassthrough(),
                "context": itemgetter("question") | self.retriever | _format_docs,
                "history": itemgetter("history"),
            }
            | self.prompt
            | self.llm
        )

        self._sync_connection = psycopg.connect(conn)
        self.chat_table_name = os.environ["CHAT_TABLE_NAME"] or "message_store"
        PostgresChatMessageHistory.create_tables(self._sync_connection, self.chat_table_name)

        # Define the history getter (uses the same DB connection)
        def get_session_history(session_id: str) -> PostgresChatMessageHistory:
            return PostgresChatMessageHistory(
                self.chat_table_name,
                session_id,
                sync_connection=self._sync_connection,
                # create_table=True,
            )

        self.chain = RunnableWithMessageHistory(
            base_chain,
            get_session_history,  # Pass the function here
            input_messages_key="question",
            history_messages_key="history",
        )

    # ---- public API

    def add_documents(self, docs: list[Document]) -> list[str]:
        """
        Add parsed resume chunks (LangChain Documents) to the collection.
        Make sure each doc.metadata['source'] is set (e.g., filename).

        Args:
            - docs: list of Document chunks to add (they will be embedded)

        Returns: list of IDs of the added documents.
        """
        for d in docs:
            d.metadata.setdefault("source", "unknown")
        return self.vs.add_documents(docs)

    def ask(self, question: str, session_id: str = "default", k: int | None = None) -> str:
        """
        Ask a question with memory (per-session).

        Args:
            - question: user question string
            - session_id: identifier for chat session (memory)
            - k: optional override for number of context docs to retrieve

        Returns:
            - str: answer string from the LLM
        """
        # Allow per-call k (adjust retriever on the fly)
        if k is None:
            k = self.k
        if k is not None:
            self.retriever = self.vs.as_retriever(
                search_kwargs={"k": k, "filter": {"session_id": {"$eq": self.session_id}}}
            )

        resp = self.chain.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}},
        )

        return getattr(resp, "content", str(resp))

    def set_session_filter(self, session_id: str):
        """
        Set the session_id filter for the retriever (for context docs).

        Args:
            - session_id: identifier for chat session (memory)
        """
        kwargs = {"k": self.k or 5, "filter": {"session_id": {"$eq": session_id}}}
        self.retriever = self.vs.as_retriever(search_kwargs=kwargs)

    def close(self):
        """Close any open resources, e.g., DB connections."""
        if self._sync_connection:
            self._sync_connection.close()
            self._sync_connection = None
