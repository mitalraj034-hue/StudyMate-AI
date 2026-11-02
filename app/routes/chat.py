import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.extra import DocumentChunk
from app.services.auth_service import get_current_user
from app.services.rag_service import RAGService
from app.services.gemini_service import gemini_service

router = APIRouter(tags=["AI Grounded Chat & RAG"])


class ChatQueryRequest(BaseModel):
    document_id: int
    query: Optional[str] = None
    question: Optional[str] = None
    custom_api_key: Optional[str] = None
    mode: Optional[str] = "Detailed Explanation"
    level: Optional[str] = "Intermediate"
    language: Optional[str] = "English"
    action: Optional[str] = None


class SummaryRequest(BaseModel):
    document_id: int
    summary_type: Optional[str] = "Detailed Summary"
    length: Optional[str] = "Detailed"
    topic: Optional[str] = None
    level: Optional[str] = "Intermediate"
    language: Optional[str] = "English"
    action: Optional[str] = None


@router.post("/chat")
@router.post("/rag/chat")
async def chat_with_document(
    req: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query_text = req.query or req.question or ""
    return await RAGService.process_chat(
        db=db,
        current_user=current_user,
        document_id=req.document_id,
        query=query_text,
        custom_api_key=req.custom_api_key,
        mode=req.mode or "Detailed Explanation",
        level=req.level or "Intermediate",
        language=req.language or "English",
        action=req.action
    )


@router.get("/chat/{doc_id}/history")
@router.get("/rag/chat/{doc_id}/history")
def get_chat_history(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return RAGService.get_document_chat_history(db, current_user, doc_id)


@router.delete("/chat/{doc_id}/history")
@router.delete("/rag/chat/{doc_id}/history")
def clear_chat_history(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return RAGService.clear_document_chat_history(db, current_user, doc_id)


@router.post("/summary")
@router.post("/rag/summary")
def generate_summary(
    req: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return RAGService.generate_summary_for_doc(
        db=db,
        current_user=current_user,
        document_id=req.document_id,
        summary_type=req.summary_type or "Detailed Summary",
        length=req.length or "Detailed",
        topic=req.topic,
        level=req.level or "Intermediate",
        language=req.language or "English",
        action=req.action
    )
