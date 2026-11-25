import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure backend directory is in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.config import settings
from app.database import init_db, get_db, SessionLocal
from swagger_theme import get_studymate_swagger_html
from app.routes import (
    auth_router,
    documents_router,
    chat_router,
    quiz_router,
    flashcards_router,
    progress_router,
    settings_router,
    gemini_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization notice: {e}")
    try:
        from seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"Startup database check: {e}")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Document-grounded AI APIs for document processing, RAG chat, summaries, quizzes, flashcards and learning progress.",
    version=settings.VERSION,
    docs_url=None,  # Replaced with custom premium StudyMate AI Swagger UI
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom Premium Swagger UI Route
@app.get("/docs", include_in_schema=False)
def custom_swagger_docs():
    return HTMLResponse(content=get_studymate_swagger_html())


# Include API Routers under /api
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(quiz_router, prefix=settings.API_V1_PREFIX)
app.include_router(flashcards_router, prefix=settings.API_V1_PREFIX)
app.include_router(progress_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)
app.include_router(gemini_router, prefix=settings.API_V1_PREFIX)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "Supabase Cloud PostgreSQL",
        "storage": "Supabase Cloud Storage (documents)",
        "vector_store": "Supabase pgvector / Gemini Embeddings",
        "ai_engine": "Google Gemini 1.5 Flash",
        "grounding": "Strict Citation RAG"
    }


# Check if frontend build exists to serve static files
frontend_dist = BACKEND_DIR.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("docs") or full_path == "openapi.json":
            raise HTTPException(status_code=404, detail="API route not found")
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to StudyMate AI Backend API!",
            "documentation": "/docs",
            "health": "/api/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
