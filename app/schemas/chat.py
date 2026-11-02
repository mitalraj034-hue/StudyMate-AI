from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    document_id: int
    query: Optional[str] = None
    question: Optional[str] = None
    custom_api_key: Optional[str] = None


class CitationOut(BaseModel):
    chunk_index: Optional[int] = None
    page_number: int
    excerpt: str
    relevance_score: Optional[float] = 0.0


class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]] = []
    confidence: Optional[str] = "High"
    grounded: bool = True
    message_id: Optional[int] = None


class ChatHistoryItem(BaseModel):
    id: int
    user_id: int
    document_id: int
    question: str
    answer: str
    citations: Optional[List[Dict[str, Any]]] = []
    created_at: datetime

    class Config:
        from_attributes = True
