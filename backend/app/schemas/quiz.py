from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class QuizGenerateRequest(BaseModel):
    document_id: int
    title: Optional[str] = None
    count: Optional[int] = 5
    difficulty: Optional[str] = "Medium"


class QuizSubmitRequest(BaseModel):
    answers: Dict[str, int]
    time_spent_seconds: Optional[int] = 45


class QuizResultOut(BaseModel):
    id: int
    user_id: int
    document_id: int
    total_questions: int
    correct_answers: int
    wrong_answers: int
    score: int
    percentage: float
    created_at: datetime

    class Config:
        from_attributes = True


class QuizSubmitResponse(BaseModel):
    attempt_id: int
    result_id: Optional[int] = None
    score: int
    total_questions: int
    percentage: float
    feedback: List[Dict[str, Any]]
