import shutil
import uuid
import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session

from database import get_db, User, Document, DocumentChunk, ActivityLog, Quiz, Flashcard
from auth import get_current_user
from config import settings
from pdf_processor import extract_text_from_pdf, chunk_document
from rag_engine import rag_engine

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = settings.UPLOAD_DIR / unique_filename

    # Save uploaded file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    file_size = file_path.stat().st_size

    # Create Document record with initial 'processing' status
    doc = Document(
        user_id=current_user.id,
        filename=unique_filename,
        original_name=file.filename,
        file_size=file_size,
        status="processing"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        # 1. Page-by-page text extraction
        extracted = extract_text_from_pdf(file_path)
        total_pages = extracted["total_pages"]
        pages_data = extracted["pages"]
        full_text = extracted["full_text"]

        if not full_text.strip():
            # If no selectable text, still keep document record but note warning
            doc.status = "ready"
            doc.page_count = total_pages
            doc.summary = "This document appears to contain scanned images or minimal selectable text. You can still test with text or try another PDF."
            db.commit()
            return {
                "message": "Document uploaded, but little selectable text was detected.",
                "document": {
                    "id": doc.id,
                    "name": doc.original_name,
                    "pages": total_pages,
                    "status": "ready"
                }
            }

        # 2. Page-preserving text chunking
        chunks = chunk_document(pages_data, chunk_size=650, chunk_overlap=100)

        # 3. Save chunks in database
        chunk_records = []
        for c in chunks:
            chunk_records.append(DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                content=c["content"]
            ))
        db.bulk_save_objects(chunk_records)
        db.commit()

        # 4. Generate Embeddings & Index in ChromaDB
        rag_engine.index_document(doc.id, chunks)

        # 5. Generate Initial Executive Summary & Key Concepts
        summary_data = rag_engine.generate_summary(full_text, pages_data)
        doc.summary = summary_data["executive_summary"]
        doc.key_points_json = json.dumps(summary_data["key_concepts"])
        doc.page_count = total_pages
        doc.chunk_count = len(chunks)
        doc.chroma_collection_name = rag_engine.get_collection_name(doc.id)
        doc.status = "ready"
        db.commit()

        # Auto-generate initial flashcards & initial quiz for immediate student readiness!
        initial_flashcards = rag_engine.generate_flashcards(chunks, count=6)
        for fc in initial_flashcards:
            flashcard_obj = Flashcard(
                document_id=doc.id,
                user_id=current_user.id,
                front=fc["front"],
                back=fc["back"],
                topic=fc["topic"],
                page_number=fc["page_number"]
            )
            db.add(flashcard_obj)

        initial_quiz_questions = rag_engine.generate_quiz(chunks, count=5)
        quiz_obj = Quiz(
            document_id=doc.id,
            user_id=current_user.id,
            title=f"Quiz: {doc.original_name}",
            topic="Document Review",
            difficulty="Medium",
            total_questions=len(initial_quiz_questions),
            questions_json=json.dumps(initial_quiz_questions)
        )
        db.add(quiz_obj)

        # Activity log
        log = ActivityLog(
            user_id=current_user.id,
            activity_type="upload",
            title=f"Uploaded '{doc.original_name}'",
            description=f"Processed {total_pages} pages into {len(chunks)} chunks and vector embeddings."
        )
        db.add(log)
        db.commit()

        return {
            "message": "Document uploaded and indexed successfully!",
            "document": {
                "id": doc.id,
                "name": doc.original_name,
                "pages": total_pages,
                "chunks": len(chunks),
                "status": "ready",
                "summary": doc.summary
            }
        }

    except Exception as e:
        doc.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("")
def list_documents(
    query: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Document).filter(Document.user_id == current_user.id)
    if query:
        q = q.filter(Document.original_name.ilike(f"%{query}%"))
    
    docs = q.order_by(Document.created_at.desc()).all()
    
    result = []
    for d in docs:
        result.append({
            "id": d.id,
            "original_name": d.original_name,
            "file_size": d.file_size,
            "page_count": d.page_count,
            "chunk_count": d.chunk_count,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
            "has_summary": bool(d.summary)
        })
    return result


@router.get("/{doc_id}")
def get_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    key_points = json.loads(doc.key_points_json) if doc.key_points_json else []
    
    return {
        "id": doc.id,
        "original_name": doc.original_name,
        "file_size": doc.file_size,
        "page_count": doc.page_count,
        "chunk_count": doc.chunk_count,
        "status": doc.status,
        "summary": doc.summary,
        "key_points": key_points,
        "created_at": doc.created_at.isoformat()
    }


@router.delete("/{doc_id}")
def delete_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove vector index from ChromaDB
    rag_engine.delete_document_index(doc.id)

    # Remove file from disk
    file_path = settings.UPLOAD_DIR / doc.filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    # Delete record from database (cascades chunks, quizzes, flashcards)
    db.delete(doc)

    log = ActivityLog(
        user_id=current_user.id,
        activity_type="delete",
        title=f"Deleted '{doc.original_name}'",
        description="Removed document and associated vector embeddings."
    )
    db.add(log)
    db.commit()

    return {"message": "Document deleted successfully"}
