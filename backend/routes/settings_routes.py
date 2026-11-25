import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, User
from auth import get_current_user
from config import settings

router = APIRouter(prefix="/settings", tags=["Settings"])


class ApiKeysRequest(BaseModel):
    anthropic_key: Optional[str] = None
    openai_key: Optional[str] = None
    gemini_key: Optional[str] = None
    default_provider: Optional[str] = None


@router.get("")
def get_system_settings(current_user: User = Depends(get_current_user)):
    has_anthropic = bool(settings.ANTHROPIC_API_KEY)
    has_openai = bool(settings.OPENAI_API_KEY)
    has_gemini = bool(settings.GEMINI_API_KEY)

    active_provider = "Claude 3 (Anthropic)" if has_anthropic else ("OpenAI GPT-4o" if has_openai else "Built-in Grounded Academic RAG Engine")

    return {
        "active_provider": active_provider,
        "has_anthropic": has_anthropic,
        "has_openai": has_openai,
        "has_gemini": has_gemini,
        "vector_db": "ChromaDB Persistent (Local)",
        "embedding_model": "StudyMate Dense Contextual Vectors (128-dim)",
        "grounding_strictness": "High (Zero Hallucination Guardrails)"
    }


@router.post("/keys")
def update_api_keys(req: ApiKeysRequest, current_user: User = Depends(get_current_user)):
    if req.anthropic_key is not None:
        settings.ANTHROPIC_API_KEY = req.anthropic_key.strip()
    if req.openai_key is not None:
        settings.OPENAI_API_KEY = req.openai_key.strip()
    if req.gemini_key is not None:
        settings.GEMINI_API_KEY = req.gemini_key.strip()
    if req.default_provider is not None:
        settings.DEFAULT_LLM_PROVIDER = req.default_provider

    return {
        "message": "AI settings updated successfully",
        "has_anthropic": bool(settings.ANTHROPIC_API_KEY),
        "has_openai": bool(settings.OPENAI_API_KEY),
        "has_gemini": bool(settings.GEMINI_API_KEY)
    }
