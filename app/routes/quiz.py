import json
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.extra import Quiz
from app.models.quiz_result import QuizResult
from app.services.auth_service import get_current_user
from app.services.rag_service import RAGService

router = APIRouter(prefix="/quiz", tags=["MCQ Quizzes"])


class GenerateQuizRequest(BaseModel):
    document_id: int
    title: Optional[str] = None
    count: Optional[int] = 5
    difficulty: Optional[str] = "Medium"
    topic: Optional[str] = None


class SubmitQuizRequest(BaseModel):
    quiz_id: Optional[int] = None
    answers: Dict[str, int]
    time_spent_seconds: Optional[int] = 45


@router.post("/generate")
def generate_quiz(
    req: GenerateQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return RAGService.generate_quiz_for_doc(
        db=db,
        current_user=current_user,
        document_id=req.document_id,
        count=req.count or 5,
        difficulty=req.difficulty or "Medium",
        title=req.title,
        topic=req.topic
    )


@router.post("/{quiz_id}/submit")
def submit_quiz_by_id(
    quiz_id: int,
    req: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return RAGService.submit_quiz_attempt(
        db=db,
        current_user=current_user,
        quiz_id=quiz_id,
        answers=req.answers,
        time_spent_seconds=req.time_spent_seconds or 60
    )


@router.post("/submit")
def submit_quiz_general(
    req: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.quiz_id:
        raise HTTPException(status_code=400, detail="quiz_id is required in submit request.")
    return RAGService.submit_quiz_attempt(
        db=db,
        current_user=current_user,
        quiz_id=req.quiz_id,
        answers=req.answers,
        time_spent_seconds=req.time_spent_seconds or 60
    )


@router.get("/{quiz_id}")
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    questions = json.loads(quiz.questions_json)
    return {
        "id": quiz.id,
        "title": quiz.title,
        "difficulty": quiz.difficulty,
        "total_questions": quiz.total_questions,
        "questions": questions,
        "created_at": quiz.created_at.isoformat()
    }


@router.get("/document/{doc_id}")
def get_document_quizzes(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quizzes = db.query(Quiz).filter(
        Quiz.document_id == doc_id,
        Quiz.user_id == current_user.id
    ).order_by(Quiz.created_at.desc()).all()

    return [
        {
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "total_questions": q.total_questions,
            "created_at": q.created_at.isoformat()
        }
        for q in quizzes
    ]
