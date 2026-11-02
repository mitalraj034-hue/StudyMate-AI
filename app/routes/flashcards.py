from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.flashcard import Flashcard
from app.models.extra import FlashcardProgress
from app.services.auth_service import get_current_user
from app.services.rag_service import RAGService

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])


class GenerateFlashcardsRequest(BaseModel):
    document_id: int
    count: Optional[int] = 8
    topic: Optional[str] = None


class UpdateMasteryRequest(BaseModel):
    status: str  # "learning", "mastered", "new", "known", "review"


@router.post("/generate")
def generate_flashcards(
    req: GenerateFlashcardsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cards = RAGService.generate_flashcards_for_doc(
        db=db,
        current_user=current_user,
        document_id=req.document_id,
        count=req.count or 8,
        topic=req.topic
    )
    return {
        "message": f"Generated {len(cards)} flashcards",
        "cards": cards
    }


@router.get("/document/{doc_id}")
def get_flashcards(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    cards = db.query(Flashcard).filter(
        Flashcard.document_id == doc_id,
        Flashcard.user_id == current_user.id
    ).order_by(Flashcard.id.asc()).all()

    result = [
        {
            "id": c.id,
            "document_id": c.document_id,
            "question": c.question,
            "answer": c.answer,
            "front": c.question,
            "back": c.answer,
            "status": c.status,
            "mastery_status": c.mastery_status,
            "topic": c.topic,
            "page_number": c.page_number,
            "created_at": c.created_at.isoformat()
        }
        for c in cards
    ]
    return {"total": len(result), "cards": result}


@router.put("/{card_id}/mastery")
@router.put("/{card_id}/status")
def update_flashcard_status(
    card_id: int,
    req: UpdateMasteryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Flashcard).filter(Flashcard.id == card_id, Flashcard.user_id == current_user.id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found.")

    raw_status = req.status.lower().strip()
    if raw_status in ("mastered", "known"):
        card.status = "known"
    elif raw_status in ("learning", "review"):
        card.status = "review"
    else:
        card.status = "new"

    card.times_reviewed = (card.times_reviewed or 0) + 1

    # Persist in flashcard_progress table
    prog = db.query(FlashcardProgress).filter(
        FlashcardProgress.user_id == current_user.id,
        FlashcardProgress.flashcard_id == card.id
    ).first()
    if not prog:
        prog = FlashcardProgress(
            user_id=current_user.id,
            flashcard_id=card.id,
            mastery_status=card.mastery_status,
            review_count=card.times_reviewed,
            last_reviewed_at=datetime.utcnow()
        )
        db.add(prog)
    else:
        prog.mastery_status = card.mastery_status
        prog.review_count = card.times_reviewed
        prog.last_reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(card)

    return {
        "id": card.id,
        "status": card.status,
        "mastery_status": card.mastery_status,
        "times_reviewed": card.times_reviewed
    }
