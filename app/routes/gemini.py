import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.extra import DocumentChunk, Quiz
from app.services.auth_service import get_optional_user
from app.services.gemini_service import gemini_service
from app.services.rag_service import RAGService

router = APIRouter(prefix="/gemini", tags=["Google Gemini AI"])


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class GeminiChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Student message or inquiry")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Previous conversation turns")
    document_id: Optional[int] = Field(default=None, description="Optional document ID for grounded context")
    system_instruction: Optional[str] = Field(default=None, description="Custom prompt instruction for the AI tutor")


class GeminiAskRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Specific academic study question")
    document_id: Optional[int] = Field(default=None, description="Target document ID to answer from")
    context: Optional[str] = Field(default=None, description="Direct text context to ground against")


class GeminiNotesRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Topic name to generate notes for")
    content: Optional[str] = Field(default=None, description="Lecture text, transcript, or raw content")
    document_id: Optional[int] = Field(default=None, description="Document ID to extract content from")
    style: Optional[str] = Field(default="comprehensive", description="Notes style: comprehensive, bullet_points, cheat_sheet")


class GeminiSummarizeRequest(BaseModel):
    content: Optional[str] = Field(default=None, description="Text to summarize")
    document_id: Optional[int] = Field(default=None, description="Document ID to summarize")
    summary_type: Optional[str] = Field(default="executive", description="executive, key_concepts, or bullet_points")
    max_length: Optional[int] = Field(default=None, description="Optional max length")


class GeminiMCQRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Topic or concept for MCQs")
    content: Optional[str] = Field(default=None, description="Syllabus text excerpt")
    document_id: Optional[int] = Field(default=None, description="Document ID to extract questions from")
    count: Optional[int] = Field(default=5, ge=1, le=20, description="Number of questions (1-20)")
    difficulty: Optional[str] = Field(default="Medium", description="Easy, Medium, or Hard")


class GeminiQuizRequest(BaseModel):
    topic: Optional[str] = Field(default=None, description="Topic title")
    content: Optional[str] = Field(default=None, description="Study content excerpt")
    document_id: Optional[int] = Field(default=None, description="Document ID")
    title: Optional[str] = Field(default=None, description="Custom quiz title")
    count: Optional[int] = Field(default=5, ge=1, le=20, description="Total questions")
    difficulty: Optional[str] = Field(default="Medium", description="Easy, Medium, Hard")
    save_to_db: Optional[bool] = Field(default=False, description="Whether to persist quiz in Supabase")


# =============================================================================
# HELPER: RETRIEVE DOCUMENT CHUNKS
# =============================================================================
def _get_document_context(db: Session, doc_id: int, user: Optional[User]) -> tuple[str, List[Dict[str, Any]]]:
    """Retrieves document record and chunks from Supabase."""
    query = db.query(Document).filter(Document.id == doc_id)
    if user:
        query = query.filter(Document.user_id == user.id)
    doc = query.first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {doc_id} was not found."
        )

    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index.asc()).all()
    chunk_dicts = [
        {"content": c.content, "page_number": c.page_number, "similarity": 95}
        for c in chunks
    ]
    return doc.filename or doc.title or "Study Material", chunk_dicts


# =============================================================================
# 1. AI CHATBOT ENDPOINT
# =============================================================================
@router.post("/chat")
async def gemini_chat(
    req: GeminiChatRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Interactive AI Study Chatbot powered by Google Gemini.
    Supports multi-turn conversations and grounding against uploaded PDFs.
    """
    context_chunks = []
    doc_title = None

    if req.document_id:
        doc_title, context_chunks = _get_document_context(db, req.document_id, user)
        # Use vector search if query is specific
        if len(req.message.strip()) > 3:
            query_emb = gemini_service.generate_embedding(req.message)
            rag_chunks = RAGService.search_chunks(db, req.document_id, query_emb, top_k=4)
            if rag_chunks:
                context_chunks = rag_chunks

    return gemini_service.chat(
        message=req.message,
        history=req.history,
        system_instruction=req.system_instruction,
        context_chunks=context_chunks,
        document_title=doc_title
    )


# =============================================================================
# 2. ASK STUDY QUESTIONS ENDPOINT
# =============================================================================
@router.post("/ask")
async def gemini_ask_question(
    req: GeminiAskRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Ask targeted academic questions with verified page citations, key takeaways,
    and confidence scores.
    """
    retrieved_chunks = []
    doc_title = None

    if req.document_id:
        doc_title, all_chunks = _get_document_context(db, req.document_id, user)
        query_emb = gemini_service.generate_embedding(req.question)
        rag_chunks = RAGService.search_chunks(db, req.document_id, query_emb, top_k=4)
        retrieved_chunks = rag_chunks if rag_chunks else all_chunks[:5]

    return gemini_service.ask_study_question(
        question=req.question,
        context=req.context,
        retrieved_chunks=retrieved_chunks,
        document_title=doc_title
    )


# =============================================================================
# 3. NOTES GENERATION ENDPOINT
# =============================================================================
@router.post("/notes")
async def gemini_generate_notes(
    req: GeminiNotesRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Generates structured, academic-grade study notes.
    Accepts topic name, raw lecture text, or document ID.
    Styles: 'comprehensive', 'bullet_points', 'cheat_sheet'.
    """
    content_to_use = req.content or req.topic or ""
    doc_title = req.topic or "Study Notes"

    if req.document_id:
        doc_title, chunks = _get_document_context(db, req.document_id, user)
        if not content_to_use:
            content_to_use = "\n\n".join([c["content"] for c in chunks[:12]])

    if not content_to_use.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a 'topic', 'content', or valid 'document_id' to generate study notes."
        )

    return gemini_service.generate_notes(
        topic_or_content=content_to_use,
        document_title=doc_title,
        style=req.style or "comprehensive"
    )


# =============================================================================
# 4. NOTES & DOCUMENT SUMMARIZATION ENDPOINT
# =============================================================================
@router.post("/summarize")
async def gemini_summarize_content(
    req: GeminiSummarizeRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Synthesizes executive summaries, key concepts, and reading metrics from notes or documents.
    """
    content = req.content or ""
    doc_title = "Study Material"

    if req.document_id:
        doc_title, chunks = _get_document_context(db, req.document_id, user)
        if not content:
            content = "\n\n".join([c["content"] for c in chunks[:15]])

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide 'content' or a valid 'document_id' to summarize."
        )

    result = gemini_service.summarize_notes(
        content=content,
        document_title=doc_title,
        summary_type=req.summary_type or "executive",
        max_length=req.max_length
    )

    # If document_id was provided and user authenticated, persist summary into Supabase
    if req.document_id and user:
        doc = db.query(Document).filter(Document.id == req.document_id, Document.user_id == user.id).first()
        if doc:
            doc.summary = result["summary"]
            doc.key_points_json = json.dumps(result["key_concepts"])
            db.commit()

    return result


# =============================================================================
# 5. MCQ GENERATION ENDPOINT
# =============================================================================
@router.post("/mcq")
async def gemini_generate_mcqs(
    req: GeminiMCQRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Generates targeted Multiple Choice Questions (MCQs) with 4 options each,
    answer index, and detailed explanations.
    """
    content = req.content or req.topic or ""

    if req.document_id:
        _, chunks = _get_document_context(db, req.document_id, user)
        if not content:
            content = "\n\n".join([c["content"] for c in chunks[:12]])

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a 'topic', 'content', or 'document_id' to generate MCQs."
        )

    questions = gemini_service.generate_mcq(
        content_or_topic=content,
        count=req.count or 5,
        difficulty=req.difficulty or "Medium"
    )

    return {
        "questions": questions,
        "total": len(questions),
        "difficulty": req.difficulty or "Medium"
    }


# =============================================================================
# 6. FULL QUIZ GENERATION ENDPOINT
# =============================================================================
@router.post("/quiz")
async def gemini_generate_quiz(
    req: GeminiQuizRequest,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Generates a full practice exam quiz. Optionally persists it to Supabase PostgreSQL.
    """
    content = req.content or req.topic or ""
    doc_title = req.title or req.topic or "Practice Exam"

    if req.document_id:
        doc_filename, chunks = _get_document_context(db, req.document_id, user)
        if not content:
            content = "\n\n".join([c["content"] for c in chunks[:15]])
        if not req.title:
            doc_title = f"{doc_filename} - {req.difficulty or 'Medium'} Quiz"

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide 'content', 'topic', or a valid 'document_id'."
        )

    quiz_result = gemini_service.generate_quiz(
        chunks_or_content=content,
        count=req.count or 5,
        difficulty=req.difficulty or "Medium",
        title=doc_title
    )

    quiz_id = None
    if req.save_to_db and req.document_id and user:
        new_quiz = Quiz(
            document_id=req.document_id,
            user_id=user.id,
            title=quiz_result["title"],
            difficulty=quiz_result["difficulty"],
            total_questions=quiz_result["total_questions"],
            questions_json=json.dumps(quiz_result["questions"])
        )
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)
        quiz_id = new_quiz.id

    return {
        "quiz_id": quiz_id,
        "title": quiz_result["title"],
        "difficulty": quiz_result["difficulty"],
        "total_questions": quiz_result["total_questions"],
        "questions": quiz_result["questions"],
        "estimated_time_minutes": quiz_result["estimated_time_minutes"]
    }
