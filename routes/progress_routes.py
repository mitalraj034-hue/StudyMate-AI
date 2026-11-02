from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, User, Document, ChatMessage, QuizAttempt, Flashcard, ActivityLog, Quiz
from auth import get_current_user

router = APIRouter(prefix="/progress", tags=["Learning Progress & Analytics"])


@router.get("/dashboard-stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Total Documents
    total_docs = db.query(Document).filter(Document.user_id == current_user.id).count()

    # Total Questions Asked (role == 'user')
    total_questions = db.query(ChatMessage).filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.role == "user"
    ).count()

    # Quizzes Completed
    quiz_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).all()
    quizzes_completed = len(quiz_attempts)

    # Average Quiz Score
    if quizzes_completed > 0:
        avg_score = round(sum(a.percentage for a in quiz_attempts) / quizzes_completed, 1)
    else:
        avg_score = 0.0

    # Total Flashcards & Mastery
    total_flashcards = db.query(Flashcard).filter(Flashcard.user_id == current_user.id).count()
    mastered_flashcards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id,
        Flashcard.mastery_status == "mastered"
    ).count()

    # Study Progress calculation (weighted composite of docs uploaded, questions asked, quiz scores, flashcards mastered)
    # E.g. base progression towards student mastery
    doc_points = min(30, total_docs * 10)
    quiz_points = min(35, int((avg_score / 100) * 35)) if quizzes_completed > 0 else 0
    fc_points = min(20, int((mastered_flashcards / (total_flashcards or 1)) * 20)) if total_flashcards > 0 else 0
    chat_points = min(15, total_questions * 3)
    study_progress = min(100, doc_points + quiz_points + fc_points + chat_points)

    # Recent Documents (up to 4)
    recent_docs = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).limit(4).all()
    recent_docs_list = [
        {
            "id": d.id,
            "name": d.original_name,
            "pages": d.page_count,
            "chunks": d.chunk_count,
            "created_at": d.created_at.isoformat()
        }
        for d in recent_docs
    ]

    # Recent Quiz Scores (up to 5)
    recent_attempts = db.query(QuizAttempt).filter(QuizAttempt.user_id == current_user.id).order_by(QuizAttempt.completed_at.desc()).limit(5).all()
    recent_scores_list = []
    for att in recent_attempts:
        quiz = db.query(Quiz).filter(Quiz.id == att.quiz_id).first()
        doc = db.query(Document).filter(Document.id == att.document_id).first()
        recent_scores_list.append({
            "id": att.id,
            "quiz_title": quiz.title if quiz else "Quiz",
            "document_name": doc.original_name if doc else "Document",
            "score": att.score,
            "total": att.total_questions,
            "percentage": att.percentage,
            "completed_at": att.completed_at.isoformat()
        })

    # Recent Activities (up to 8)
    activities = db.query(ActivityLog).filter(ActivityLog.user_id == current_user.id).order_by(ActivityLog.created_at.desc()).limit(8).all()
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

    # "Continue Studying" recommended document
    continue_doc = None
    if recent_docs:
        d = recent_docs[0]
        continue_doc = {
            "id": d.id,
            "name": d.original_name,
            "pages": d.page_count,
            "summary": (d.summary[:150] + "...") if d.summary else "Ready for study and quiz revision."
        }

    return {
        "metrics": {
            "total_documents": total_docs,
            "total_questions_asked": total_questions,
            "quizzes_completed": quizzes_completed,
            "average_quiz_score": avg_score,
            "study_progress": study_progress,
            "total_flashcards": total_flashcards,
            "mastered_flashcards": mastered_flashcards
        },
        "recent_documents": recent_docs_list,
        "recent_quiz_scores": recent_scores_list,
        "activities": activities_list,
        "continue_studying": continue_doc
    }
