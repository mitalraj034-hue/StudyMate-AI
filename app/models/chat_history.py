from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    citations = Column(Text, nullable=True)  # JSON-stringified citation objects
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # SQLAlchemy Relationships
    user = relationship("User", back_populates="chat_history")
    document = relationship("Document", back_populates="chat_history")

    def __repr__(self):
        return f"<ChatHistory id={self.id} user_id={self.user_id} document_id={self.document_id}>"
