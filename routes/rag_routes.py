import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, User, Document, DocumentChunk, ChatMessage, ActivityLog
from auth import get_current_user
from rag_engine import rag_engine

router = APIRouter(prefix="/rag", tags=["RAG AI Services"])


class ChatQueryRequest(BaseModel):
    document_id: int
    query: str
    custom_api_key: Optional[str] = None


class SummaryRequest(BaseModel):
    document_id: int


@router.post("/chat")
async def chat_with_document(
    req: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Save user question
    user_msg = ChatMessage(
        document_id=doc.id,
        user_id=current_user.id,
        role="user",
        content=req.query
    )
    db.add(user_msg)
    db.commit()

    # 2. Query RAG engine for grounded answer with citations
    rag_result = await rag_engine.answer_question(
        doc_id=doc.id,
        query=req.query,
        custom_api_key=req.custom_api_key
    )

    # 3. Save assistant response with page citations
    citations_json = json.dumps(rag_result.get("citations", []))
    bot_msg = ChatMessage(
        document_id=doc.id,
        user_id=current_user.id,
        role="assistant",
        content=rag_result["answer"],
        citations_json=citations_json
    )
    db.add(bot_msg)

    # Activity log
    log = ActivityLog(
        user_id=current_user.id,
        activity_type="chat",
        title=f"Asked: '{req.query[:45]}...'",
        description=f"Received grounded answer citing {len(rag_result.get('citations', []))} pages."
    )
    db.add(log)
    db.commit()

    return {
        "answer": rag_result["answer"],
        "citations": rag_result["citations"],
        "confidence": rag_result["confidence"],
        "grounded": rag_result["grounded"],
        "message_id": bot_msg.id
    }


@router.get("/chat/{doc_id}/history")
def get_chat_history(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    messages = db.query(ChatMessage).filter(
        ChatMessage.document_id == doc_id,
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.asc()).all()

    result = []
    for m in messages:
        citations = json.loads(m.citations_json) if m.citations_json else []
        result.append({
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "citations": citations,
            "created_at": m.created_at.isoformat()
        })
    return result


@router.post("/summary")
def generate_detailed_summary(
    req: SummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index.asc()).all()
    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks found for this document.")

    # Reconstruct page text
    pages_dict = {}
    for c in chunks:
        pages_dict.setdefault(c.page_number, []).append(c.content)

    pages_data = [{"page_number": p, "text": " ".join(texts)} for p, texts in sorted(pages_dict.items())]
    full_text = "\n\n".join(p["text"] for p in pages_data)

    summary_result = rag_engine.generate_summary(full_text, pages_data)

    # Update document record
    doc.summary = summary_result["executive_summary"]
    doc.key_points_json = json.dumps(summary_result["key_concepts"])
    db.commit()

    return summary_result
