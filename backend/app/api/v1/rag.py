from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.interaction import ChatHistory
from app.services.rag_service import RAGService

router = APIRouter(prefix="/rag", tags=["RAG & AI Assistant Engine"])

class RAGQueryRequest(BaseModel):
    query: str
    explanation_level: Optional[str] = "simple"  # legal | simple | eli10

@router.post("/query")
async def process_rag_query(
    req: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rag_service = RAGService(db)
    return await rag_service.execute_rag_pipeline(
        user_id=current_user.id,
        query=req.query,
        explanation_level=req.explanation_level or "simple"
    )

@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(20)
    )
    chats = result.scalars().all()
    return [
        {
            "id": c.id,
            "query": c.query,
            "explanation_level": c.explanation_level,
            "response": c.response,
            "sources": c.sources_json,
            "scam_flagged": c.scam_flagged,
            "confidence_score": c.confidence_score,
            "created_at": c.created_at
        }
        for c in chats
    ]
