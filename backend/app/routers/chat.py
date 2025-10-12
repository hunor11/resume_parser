# app/routers/chat.py
from __future__ import annotations

from app.services.resume_agent_service import ResumeAgent
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


@router.post("/")
def chat(req: ChatRequest):
    """
    Chat with the ResumeAgent. Retrieval is filtered to this session_id, so
    only documents uploaded in this session are visible to the bot.
    """
    agent = ResumeAgent(session_id=req.session_id)
    # uses env: VECTOR_DB_URL, GOOGLE_API_KEY

    try:
        answer = agent.ask(req.message, session_id=req.session_id)
        return {"session_id": req.session_id, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        agent.close()
