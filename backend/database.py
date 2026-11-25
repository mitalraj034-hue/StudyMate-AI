"""
StudyMate AI Database Gateway
Provides unified access to SQLAlchemy engine, sessions, Base, and models
defined in app.database and app.models.
"""

from app.database import engine, SessionLocal, Base, get_db, init_db
from app.models import (
    User,
    Document,
    ChatHistory,
    QuizResult,
    Flashcard,
    DocumentChunk,
    Quiz,
    QuizAttempt,
    QuizAnswer,
    ChatMessage,
    ActivityLog,
    Summary,
    FlashcardSet,
    FlashcardProgress
)

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "init_db",
    "User",
    "Document",
    "ChatHistory",
    "QuizResult",
    "Flashcard",
    "DocumentChunk",
    "Quiz",
    "QuizAttempt",
    "QuizAnswer",
    "ChatMessage",
    "ActivityLog",
    "Summary",
    "FlashcardSet",
    "FlashcardProgress",
]
