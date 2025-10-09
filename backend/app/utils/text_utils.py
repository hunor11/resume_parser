import re

from langchain.text_splitter import RecursiveCharacterTextSplitter


def clean_text(text: str) -> str:
    """Normalize whitespace, remove control chars and excessive breaks."""
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 400,
    chunk_overlap: int = 50,
) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_text(text)


def count_tokens(text: str) -> int:
    """Approximate token count (word-based fallback)."""
    return len(text.split())
