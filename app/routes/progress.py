from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.chat_history import ChatHistory
from app.models.quiz_result import QuizResult
from app.models.flashcard import Flashcard
from app.models.extra import ActivityLog, QuizAttempt, ChatMessage, Quiz
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/progress", tags=["Learning Progress & Analytics"])


@router.get("")
@router.get("/")
@router.get("/dashboard-stats")
def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculates study progress, metrics, and analytics from PostgreSQL tables."""
    # 1. Total Documents
    total_docs = db.query(Document).filter(Document.user_id == current_user.id).count()

    # 2. Total Questions asked (from ChatHistory + ChatMessage)
    chat_hist_count = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).count()
    legacy_chat_count = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.role == "user"
    ).count()
    total_questions = max(chat_hist_count, legacy_chat_count)

    # 3. Quiz Results & Scoring
    quiz_results = db.query(QuizResult).filter(QuizResult.user_id == current_user.id).all()
    legacy_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()

    quizzes_completed = len(quiz_results) if len(quiz_results) > 0 else len(legacy_attempts)

    if len(quiz_results) > 0:
        avg_score = round(sum(r.percentage for r in quiz_results) / len(quiz_results), 1)
    elif len(legacy_attempts) > 0:
        avg_score = round(sum(a.percentage for a in legacy_attempts) / len(legacy_attempts), 1)
    else:
        avg_score = 0.0

    # 4. Flashcards and mastery
    total_flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).count()
    mastered_flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id,
        Flashcard.status.in_(["known", "mastered"])
    ).count()

    # 5. Composite Learning Progress (0-100%)
    doc_points = min(30, total_docs * 10)
    quiz_points = min(35, int((avg_score / 100) * 35)) if quizzes_completed > 0 else 0
    fc_points = min(20, int((mastered_flashcards / (total_flashcards or 1)) * 20)) if total_flashcards > 0 else 0
    chat_points = min(15, total_questions * 3)
    study_progress = min(100, doc_points + quiz_points + fc_points + chat_points)

    # 6. Recent Documents
    recent_docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).limit(4).all()

    recent_docs_list = [
        {
            "id": d.id,
            "name": d.original_filename,
            "original_filename": d.original_filename,
            "pages": d.page_count,
            "chunks": d.chunk_count,
            "created_at": d.created_at.isoformat()
        }
        for d in recent_docs
    ]

    # 7. Recent Quiz Scores
    recent_scores_list = []
    if len(quiz_results) > 0:
        recent_res = db.query(QuizResult).filter(
            QuizResult.user_id == current_user.id
        ).order_by(QuizResult.created_at.desc()).limit(5).all()

        for r in recent_res:
            doc = db.query(Document).filter(Document.id == r.document_id).first()
            recent_scores_list.append({
                "id": r.id,
                "quiz_title": f"Quiz for {doc.original_filename if doc else 'Document'}",
                "document_name": doc.original_filename if doc else "Document",
                "score": r.score,
                "total_questions": r.total_questions,
                "percentage": r.percentage,
                "completed_at": r.created_at.isoformat()
            })
    else:
        for att in legacy_attempts[-5:]:
            quiz = db.query(Quiz).filter(Quiz.id == att.quiz_id).first()
            doc = db.query(Document).filter(Document.id == att.document_id).first()
            recent_scores_list.append({
                "id": att.id,
                "quiz_title": quiz.title if quiz else "Quiz",
                "document_name": doc.original_filename if doc else "Document",
                "score": att.score,
                "total_questions": att.total_questions,
                "percentage": att.percentage,
                "completed_at": att.completed_at.isoformat()
            })

    # 8. Recent Activities
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.created_at.desc()).limit(6).all()

    activities_list = [
        {
            "id": a.id,
            "type": a.activity_type,
            "title": a.title,
            "description": a.description,
            "created_at": a.created_at.isoformat()
        }
        for a in activities
    ]

    return {
        "metrics": {
            "total_documents": total_docs,
            "questions_asked": total_questions,
            "quizzes_completed": quizzes_completed,
            "avg_quiz_score": avg_score,
            "flashcards_total": total_flashcards,
            "flashcards_mastered": mastered_flashcards,
            "study_progress": study_progress
        },
        "recent_documents": recent_docs_list,
        "recent_quiz_scores": recent_scores_list,
        "recent_activities": activities_list
    }
