from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, synonym
from app.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    status = Column(String(50), default="new", nullable=False)  # new, known, review
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Optional metadata for study cards UI
    page_number = Column(Integer, default=1, nullable=True)
    topic = Column(String(255), default="Key Concept", nullable=True)
    times_reviewed = Column(Integer, default=0, nullable=True)

    # Compatibility synonyms for existing frontend
    front = synonym("question")
    back = synonym("answer")

    @property
    def mastery_status(self) -> str:
        return "mastered" if self.status == "known" else "learning"

    @mastery_status.setter
    def mastery_status(self, val: str):
        if val == "mastered":
            self.status = "known"
        else:
            self.status = "review"

    # SQLAlchemy Relationships
    user = relationship("User", back_populates="flashcards")
    document = relationship("Document", back_populates="flashcards")

    def __repr__(self):
        return f"<Flashcard id={self.id} user_id={self.user_id} status='{self.status}'>"
