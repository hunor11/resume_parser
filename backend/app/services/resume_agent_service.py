# resume_agent.py
from __future__ import annotations

import os
from operator import itemgetter

from dotenv import load_dotenv
from langchain.schema import Document
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector


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
        collection_name: str = "resumes",
        k: int = 5,
    ) -> None:
        """
        Args:
            - collection_name: pgvector collection (table) name
            - k: number of context docs to retrieve per query

        Note: requires VECTOR_DB_URL and GEMINI_API_KEY in env.
        """
        load_dotenv()
        conn = os.environ["VECTOR_DB_URL"]
        if conn.startswith("postgres://"):  # aiven gives this URL format :(
            conn = conn.replace("postgres://", "postgresql+psycopg://", 1)

        self.emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        self.vs = PGVector(
            connection=conn,
            collection_name=collection_name,
            embeddings=self.emb,
        )
        self.retriever = self.vs.as_retriever(search_kwargs={"k": k})

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2,  # set a low temperature for more factual responses
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

        self._store: dict[str, ChatMessageHistory] = {}

        def _get_session_history(session_id: str) -> ChatMessageHistory:
            if session_id not in self._store:
                self._store[session_id] = ChatMessageHistory()
            return self._store[session_id]

        self.chain = RunnableWithMessageHistory(
            base_chain,
            _get_session_history,
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
        """
        # Allow per-call k (adjust retriever on the fly)
        if k is not None:
            self.retriever = self.vs.as_retriever(search_kwargs={"k": k})

        resp = self.chain.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}},
        )
        # resp is a ChatMessage; return text content
        return getattr(resp, "content", str(resp))

    def reset_session(self, session_id: str = "default") -> None:
        """Clear the conversation history for a given session_id."""
        self._store.pop(session_id, None)
