# app/routers/uploads.py
from __future__ import annotations

import os
from pathlib import Path

from app.services.parsing_service import ParsingService
from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector

router = APIRouter(prefix="/upload", tags=["upload"])

load_dotenv()
# expects VECTOR_DB_URL,
# EMBEDDING_MODEL optional,
# RESUME_COLLECTION optional
# UPLOAD_ROOT optional

RAW_URL = os.environ["VECTOR_DB_URL"]
if RAW_URL.startswith("postgres://"):
    RAW_URL = RAW_URL.replace("postgres://", "postgresql+psycopg://", 1)

EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# Single collection for everyone; we scope by metadata "session_id"
COLLECTION = os.getenv("RESUME_COLLECTION", "resumes")
vs = PGVector(connection=RAW_URL, collection_name=COLLECTION, embeddings=emb)

# Where to temporarily save uploads (use per-session subfolders)
UPLOAD_ROOT = Path(os.getenv("UPLOAD_ROOT", "data/uploads"))
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

parser = ParsingService()


@router.post("/")
async def upload_files(
    session_id: str = Form(..., min_length=1),
    files: list[UploadFile] = None,
):
    """
    Upload TXT/PDF files, parse+chunk, and index them into PGVector with metadata
    `session_id` so they are only retrieved for that user's session.
    """
    if files is None:
        files = File(...)
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    saved = 0
    indexed = 0

    sess_dir = UPLOAD_ROOT / session_id
    sess_dir.mkdir(parents=True, exist_ok=True)

    for f in files:
        suffix = Path(f.filename).suffix.lower()
        if suffix not in {".txt", ".pdf"}:
            raise HTTPException(status_code=415, detail=f"Unsupported type: {suffix}")

        path = sess_dir / f.filename
        with open(path, "wb") as out:
            out.write(await f.read())
        saved += 1

        chunks = parser.parse_single(path)
        if not chunks:
            continue

        for d in chunks:
            d.metadata.setdefault("source", f.filename)
            d.metadata["session_id"] = session_id

        vs.add_documents(chunks)
        indexed += len(chunks)

    return {"session_id": session_id, "files_saved": saved, "chunks_indexed": indexed}
