from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, synonym
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=True)  # Reference to file object in Supabase Storage
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=0)
    status = Column(String(50), default="processing")  # uploading, processing, completed, failed, ready
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # RAG metadata and summaries
    summary = Column(Text, nullable=True)
    key_points_json = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    chroma_collection_name = Column(String(255), nullable=True)

    # Compatibility synonym
    original_name = synonym("original_filename")

    # SQLAlchemy Relationships
    user = relationship("User", back_populates="documents")
    chat_history = relationship("ChatHistory", back_populates="document", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="document", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="document", cascade="all, delete-orphan")

    # Additional application relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="document", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="document", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document id={self.id} user_id={self.user_id} filename='{self.original_filename}'>"
