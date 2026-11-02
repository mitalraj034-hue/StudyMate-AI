from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, User, Document, DocumentChunk, Flashcard, ActivityLog
from auth import get_current_user
from rag_engine import rag_engine

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


class GenerateFlashcardsRequest(BaseModel):
    document_id: int
    count: Optional[int] = 8


class UpdateMasteryRequest(BaseModel):
    status: str # "learning" or "mastered"


@router.post("/generate")
def generate_flashcards(
    req: GenerateFlashcardsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
    if not chunks:
        raise HTTPException(status_code=400, detail="Document has no processed content.")

    chunk_dicts = [{"chunk_index": c.chunk_index, "page_number": c.page_number, "content": c.content} for c in chunks]
    generated_cards = rag_engine.generate_flashcards(chunk_dicts, count=req.count or 8)

    created_cards = []
    for fc in generated_cards:
        card = Flashcard(
            document_id=doc.id,
            user_id=current_user.id,
            front=fc["front"],
            back=fc["back"],
            topic=fc["topic"],
            page_number=fc["page_number"]
        )
        db.add(card)
        created_cards.append(card)

    log = ActivityLog(
        user_id=current_user.id,
        activity_type="flashcard",
        title=f"Generated {len(created_cards)} Flashcards",
        description=f"Created study cards for '{doc.original_name}'."
    )
    db.add(log)
    db.commit()

    return {
        "message": f"Generated {len(created_cards)} flashcards",
        "cards": [
            {
                "id": c.id,
                "front": c.front,
                "back": c.back,
                "topic": c.topic,
                "page_number": c.page_number,
                "mastery_status": c.mastery_status,
                "times_reviewed": c.times_reviewed
            }
            for c in created_cards
        ]
    }


@router.get("/document/{doc_id}")
def get_document_flashcards(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cards = db.query(Flashcard).filter(Flashcard.document_id == doc_id, Flashcard.user_id == current_user.id).order_by(Flashcard.id.asc()).all()
    
    total = len(cards)
    mastered = sum(1 for c in cards if c.mastery_status == "mastered")
    
    return {
        "total": total,
        "mastered": mastered,
        "learning": total - mastered,
        "mastery_percentage": round((mastered / total * 100) if total > 0 else 0, 1),
        "cards": [
            {
                "id": c.id,
                "front": c.front,
                "back": c.back,
                "topic": c.topic,
                "page_number": c.page_number,
                "mastery_status": c.mastery_status,
                "times_reviewed": c.times_reviewed
            }
            for c in cards
        ]
    }


@router.put("/{card_id}/mastery")
def update_flashcard_mastery(
    card_id: int,
    req: UpdateMasteryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found.")

    card.mastery_status = req.status
    card.times_reviewed = (card.times_reviewed or 0) + 1
    db.commit()

    return {
        "id": card.id,
        "mastery_status": card.mastery_status,
        "times_reviewed": card.times_reviewed
    }
