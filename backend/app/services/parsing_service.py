from __future__ import annotations

from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.document_loaders.base import BaseLoader


class ParsingService:
    """
    Loading + chunking (no counts). Use:
      - parse_single(path) -> List[Document]  (chunks)
      - parse_directory()  -> Dict[filename, List[Document]] (chunks per file)
    """

    SUPPORTED_EXT = {".pdf", ".txt"}

    def __init__(
        self,
        data_dir: str | Path = "data/resumes",
        chunk_size: int = 400,
        chunk_overlap: int = 50,
    ) -> None:
        """
        Args:
            - data_dir: directory with resume files (PDF or TXT)
            - chunk_size: max tokens per chunk
            - chunk_overlap: tokens of overlap between chunks
        Note: uses RecursiveCharacterTextSplitter (LangChain) for chunking.
        """
        self.data_dir = Path(data_dir)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def _load_document(self, file_path: Path) -> list[Document]:
        """Load a single document (PDF or TXT) into LangChain Document objects."""
        ext = file_path.suffix.lower()
        loader: BaseLoader | None = None
        if ext == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif ext == ".txt":
            loader = TextLoader(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        return loader.load()

    def _split_documents(self, docs: list[Document]) -> list[Document]:
        """Split documents into chunks."""
        return self.splitter.split_documents(docs)

    def parse_single(self, file_path: str | Path) -> list[Document]:
        """
        Parse and chunk a single resume file.
        Returns: list of Document chunks (with .page_content + .metadata)
        """
        path = Path(file_path)
        docs = self._load_document(path)
        chunks = self._split_documents(docs)
        # Ensure source filename is available in metadata on every chunk
        for ch in chunks:
            ch.metadata.setdefault("source", str(path))
        return chunks

    def parse_directory(self) -> dict[str, list[Document]]:
        """
        Parse and chunk all supported files in the directory.
        Returns: { filename: [Document, ...] }
        """
        results: dict[str, list[Document]] = {}
        for file_path in self.data_dir.glob("*"):
            if file_path.suffix.lower() not in self.SUPPORTED_EXT:
                continue
            try:
                docs = self._load_document(file_path)
                chunks = self._split_documents(docs)
                for ch in chunks:
                    ch.metadata.setdefault("source", str(file_path))
                results[file_path.name] = chunks
            except Exception:
                results[file_path.name] = []
        return results
