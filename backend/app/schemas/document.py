from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    page_count: int
    status: str


class DocumentOut(BaseModel):
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_size: int
    page_count: int
    status: str
    chunk_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentDetailOut(DocumentOut):
    summary: Optional[str] = None
    key_points: Optional[List[str]] = []
