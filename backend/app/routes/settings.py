import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.services.auth_service import get_current_user
from app.config import settings

router = APIRouter(prefix="/settings", tags=["Settings"])


class ProviderUpdateRequest(BaseModel):
    provider: str
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None


@router.get("")
@router.get("/")
def get_user_settings(current_user: User = Depends(get_current_user)):
    return {
        "active_provider": "Google Gemini AI (Grounded Academic RAG)",
        "database": "Supabase Cloud PostgreSQL",
        "storage": "Supabase Cloud Storage (documents)",
        "vector_engine": "Supabase pgvector (768-dim Gemini Embeddings)",
        "has_claude_key": bool(settings.CLAUDE_API_KEY),
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_gemini_key": bool(settings.GEMINI_API_KEY),
        "supabase_configured": bool(settings.SUPABASE_URL),
        "grounding_strictness": "Strict Citation Only",
        "embedding_model": "Google Gemini text-embedding-004",
        "user_email": current_user.email
    }


@router.post("/keys")
def update_provider_keys(
    req: ProviderUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    if req.claude_api_key:
        os.environ["CLAUDE_API_KEY"] = req.claude_api_key.strip()
        settings.CLAUDE_API_KEY = req.claude_api_key.strip()
    if req.openai_api_key:
        os.environ["OPENAI_API_KEY"] = req.openai_api_key.strip()
        settings.OPENAI_API_KEY = req.openai_api_key.strip()
    if req.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = req.gemini_api_key.strip()
        settings.GEMINI_API_KEY = req.gemini_api_key.strip()
    return {"message": "API Keys saved successfully for this session."}
