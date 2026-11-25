import json
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, User, Document, DocumentChunk, Quiz, QuizAttempt, ActivityLog
from auth import get_current_user
from rag_engine import rag_engine

router = APIRouter(prefix="/quiz", tags=["MCQ Quizzes"])


class GenerateQuizRequest(BaseModel):
    document_id: int
    title: Optional[str] = None
    count: Optional[int] = 5
    difficulty: Optional[str] = "Medium"


class SubmitQuizRequest(BaseModel):
    answers: Dict[str, int] # e.g. {"1": 2, "2": 0}
    time_spent_seconds: Optional[int] = 45


@router.post("/generate")
def generate_quiz(
    req: GenerateQuizRequest,
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
    questions = rag_engine.generate_quiz(chunk_dicts, count=req.count or 5, difficulty=req.difficulty or "Medium")

    title = req.title or f"Quiz: {doc.original_name} ({req.difficulty or 'Medium'})"
    new_quiz = Quiz(
        document_id=doc.id,
        user_id=current_user.id,
        title=title,
        difficulty=req.difficulty or "Medium",
        total_questions=len(questions),
        questions_json=json.dumps(questions)
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    log = ActivityLog(
        user_id=current_user.id,
        activity_type="quiz",
        title=f"Generated Quiz: '{title}'",
        description=f"Created {len(questions)} MCQ questions from '{doc.original_name}'."
    )
    db.add(log)
    db.commit()

    return {
        "id": new_quiz.id,
        "title": new_quiz.title,
        "difficulty": new_quiz.difficulty,
        "total_questions": new_quiz.total_questions,
        "questions": questions,
        "created_at": new_quiz.created_at.isoformat()
    }


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
        "document_id": quiz.document_id,
        "title": quiz.title,
        "difficulty": quiz.difficulty,
        "total_questions": quiz.total_questions,
        "questions": questions,
        "created_at": quiz.created_at.isoformat()
    }


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: int,
    req: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    questions = json.loads(quiz.questions_json)
    correct_count = 0
    feedback = []

    for q in questions:
        q_id_str = str(q["id"])
        user_choice = req.answers.get(q_id_str)
        is_correct = (user_choice == q["correct_index"])
        if is_correct:
            correct_count += 1
        
        feedback.append({
            "id": q["id"],
            "question": q["question"],
            "user_choice": user_choice,
            "correct_index": q["correct_index"],
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
            "page_number": q.get("page_number", 1)
        })

    total = len(questions)
    percentage = round((correct_count / total * 100) if total > 0 else 0, 1)

    attempt = QuizAttempt(
        quiz_id=quiz.id,
        document_id=quiz.document_id,
        user_id=current_user.id,
        score=correct_count,
        total_questions=total,
        percentage=percentage,
        answers_json=json.dumps(req.answers),
        time_spent_seconds=req.time_spent_seconds or 60
    )
    db.add(attempt)

    log = ActivityLog(
        user_id=current_user.id,
        activity_type="quiz",
        title=f"Completed Quiz: {percentage}%",
        description=f"Scored {correct_count}/{total} in '{quiz.title}'."
    )
    db.add(log)
    db.commit()

    return {
        "attempt_id": attempt.id,
        "score": correct_count,
        "total_questions": total,
        "percentage": percentage,
        "feedback": feedback
    }


@router.get("/document/{doc_id}")
def list_quizzes_for_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quizzes = db.query(Quiz).filter(Quiz.document_id == doc_id, Quiz.user_id == current_user.id).order_by(Quiz.created_at.desc()).all()
    result = []
    for q in quizzes:
        last_attempt = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == q.id).order_by(QuizAttempt.completed_at.desc()).first()
        result.append({
            "id": q.id,
            "title": q.title,
            "difficulty": q.difficulty,
            "total_questions": q.total_questions,
            "created_at": q.created_at.isoformat(),
            "last_score": last_attempt.percentage if last_attempt else None
        })
    return result
