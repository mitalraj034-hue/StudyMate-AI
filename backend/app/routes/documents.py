import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.extra import DocumentChunk
from app.services.auth_service import get_current_user
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    unique_name, file_path, file_size, file_bytes = DocumentService.save_upload_file(file)
    doc = DocumentService.process_and_index_document(
        db=db,
        current_user=current_user,
        unique_filename=unique_name,
        original_filename=file.filename,
        temp_file_path=file_path,
        file_size=file_size,
        file_bytes=file_bytes
    )

    return {
        "message": f"Successfully uploaded and indexed '{doc.original_filename}'.",
        "document": {
            "id": doc.id,
            "name": doc.original_filename,
            "original_filename": doc.original_filename,
            "filename": doc.filename,
            "page_count": doc.page_count,
            "chunk_count": doc.chunk_count,
            "file_size": doc.file_size,
            "status": doc.status,
            "summary": doc.summary,
            "created_at": doc.created_at.isoformat()
        }
    }


@router.get("")
@router.get("/")
def list_documents(
    query: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return documents belonging ONLY to the logged-in user."""
    docs = DocumentService.get_user_documents(db, current_user.id)
    if query:
        q_lower = query.strip().lower()
        docs = [d for d in docs if q_lower in (d.original_filename or "").lower()]
    return [
        {
            "id": d.id,
            "name": d.original_filename,
            "original_filename": d.original_filename,
            "filename": d.filename,
            "page_count": d.page_count,
            "chunk_count": d.chunk_count,
            "file_size": d.file_size,
            "status": d.status,
            "summary": d.summary,
            "created_at": d.created_at.isoformat()
        }
        for d in docs
    ]


@router.get("/{doc_id}")
def get_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = DocumentService.get_document_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    key_points = json.loads(doc.key_points_json) if doc.key_points_json else []
    return {
        "id": doc.id,
        "name": doc.original_filename,
        "original_filename": doc.original_filename,
        "filename": doc.filename,
        "page_count": doc.page_count,
        "chunk_count": doc.chunk_count,
        "file_size": doc.file_size,
        "status": doc.status,
        "summary": doc.summary,
        "key_points": key_points,
        "created_at": doc.created_at.isoformat()
    }


@router.get("/{doc_id}/pages")
def get_document_pages(
    doc_id: int,
    page: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = DocumentService.get_document_by_id(db, doc_id, current_user.id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    query = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id)
    if page:
        query = query.filter(DocumentChunk.page_number == page)
    chunks = query.order_by(DocumentChunk.chunk_index.asc()).all()

    pages_dict = {}
    for c in chunks:
        pages_dict.setdefault(c.page_number, []).append(c.content)

    return [{"page_number": p, "text": " ".join(texts)} for p, texts in sorted(pages_dict.items())]


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = DocumentService.delete_document(db, doc_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")
    return {"message": "Document and all associated vector embeddings deleted successfully."}
