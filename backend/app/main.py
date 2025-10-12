from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, uploads

origins = [
    "http://localhost:3000",  # Your Next.js frontend address
    "http://127.0.0.1:3000",
]

app = FastAPI(title="AI Resume Analyzer", version="0.1.0")
app.include_router(uploads.router)
app.include_router(chat.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
