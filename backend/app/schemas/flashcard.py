from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class FlashcardCreate(BaseModel):
    document_id: int
    count: Optional[int] = 8


class FlashcardOut(BaseModel):
    id: int
    user_id: int
    document_id: int
    question: str
    answer: str
    status: str
    created_at: datetime
    # Compatibility fields
    front: Optional[str] = None
    back: Optional[str] = None
    mastery_status: Optional[str] = None
    topic: Optional[str] = None
    page_number: Optional[int] = 1

    class Config:
        from_attributes = True


class FlashcardUpdateStatus(BaseModel):
    status: str  # "new", "known", "review" or "mastered", "learning"
