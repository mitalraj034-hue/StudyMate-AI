from app.routes.auth import router as auth_router
from app.routes.documents import router as documents_router
from app.routes.chat import router as chat_router
from app.routes.quiz import router as quiz_router
from app.routes.flashcards import router as flashcards_router
from app.routes.progress import router as progress_router
from app.routes.settings import router as settings_router
from app.routes.gemini import router as gemini_router

__all__ = [
    "auth_router",
    "documents_router",
    "chat_router",
    "quiz_router",
    "flashcards_router",
    "progress_router",
    "settings_router",
    "gemini_router",
]
