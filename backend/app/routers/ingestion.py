from pathlib import Path

from app.services.parsing_service import ParsingService
from fastapi import APIRouter, File, UploadFile

router = APIRouter(prefix="/ingest", tags=["ingestion"])
parser = ParsingService(data_dir="data/resumes")


@router.post("/directory")
def ingest_directory() -> dict[str, int]:
    """Parse all resumes in local data/resumes folder."""
    return {"parsed_files": parser.parse_directory()}


@router.post("/single")
async def ingest_single(file: UploadFile = None):
    """
    Upload a single file (PDF/TXT), parse & chunk it on the fly.
    """
    if file is None:
        file = File(...)

    temp_path = Path("data/uploads") / file.filename
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    chunks = parser.parse_single(temp_path)
    return {"filename": file.filename, "chunk_count": len(chunks)}
