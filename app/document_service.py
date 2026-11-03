import uuid
import json
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.document import Document
from app.models.extra import DocumentChunk, ActivityLog, Summary
from app.models.user import User
from pdf_processor import extract_text_from_pdf, chunk_document
from app.services.gemini_service import gemini_service
from app.services.supabase_service import supabase_service
from rag_engine import RAGEngine

rag_engine = RAGEngine()


class DocumentService:
    """
    Manages document upload to Supabase Storage, page-by-page OCR extraction,
    pgvector semantic dense embeddings with Gemini, and cloud persistence.
    """

    @staticmethod
    def save_upload_file(file: UploadFile) -> tuple[str, Path, int, bytes]:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        # Temporary buffer path for text extraction
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        temp_file_path = settings.UPLOAD_DIR / f"temp_{unique_filename}"

        try:
            file_bytes = file.file.read()
            with open(temp_file_path, "wb") as buffer:
                buffer.write(file_bytes)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")

        file_size = len(file_bytes)
        return unique_filename, temp_file_path, file_size, file_bytes

    @staticmethod
    def process_and_index_document(
        db: Session,
        current_user: User,
        unique_filename: str,
        original_filename: str,
        temp_file_path: Path,
        file_size: int,
        file_bytes: Optional[bytes] = None
    ) -> Document:
        # 1. Upload original PDF to Supabase Cloud Storage
        if file_bytes is None and temp_file_path.exists():
            with open(temp_file_path, "rb") as f:
                file_bytes = f.read()

        storage_path = supabase_service.upload_pdf_to_storage(
            file_path_in_bucket=unique_filename,
            file_bytes=file_bytes or b"",
            content_type="application/pdf"
        )

        # 2. Create initial Document record in PostgreSQL
        doc = Document(
            user_id=current_user.id,
            filename=unique_filename,
            original_filename=original_filename,
            storage_path=storage_path,
            file_path=None, # Persistent local file storage disabled; stored in Supabase Storage
            file_size=file_size,
            status="processing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # 3. Extract text from PDF page by page with chapter detection
            extracted = extract_text_from_pdf(temp_file_path)
            total_pages = extracted["total_pages"]
            pages_data = extracted["pages"]
            full_text = extracted["full_text"]
            chapters = extracted.get("chapters", [])

            doc.page_count = total_pages

            if not full_text.strip():
                doc.status = "completed"
                doc.summary = "No extractable text was found in this document (it may contain scanned image pages)."
                db.commit()
                # Clean up temp file immediately
                if temp_file_path.exists():
                    temp_file_path.unlink()
                return doc

            # 4. Chunk text with page and chapter tracking
            chunks = chunk_document(pages_data, chapters=chapters, chunk_size=650, chunk_overlap=100)

            # 5. Generate 768-dim dense embeddings via Gemini for each chunk
            chunk_objs = []
            supabase_chunks_payload = []
            for c in chunks:
                emb = gemini_service.generate_embedding(c["content"])
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=c["chunk_index"],
                    page_number=c["page_number"],
                    content=c["content"],
                    embedding_json=json.dumps(emb)
                )
                chunk_objs.append(chunk_obj)
                supabase_chunks_payload.append({
                    "document_id": doc.id,
                    "chunk_index": c["chunk_index"],
                    "page_number": c["page_number"],
                    "content": c["content"],
                    "embedding": emb,
                    "metadata": {"source": original_filename}
                })

            db.bulk_save_objects(chunk_objs)
            db.commit()

            # 6. Index document chunks into ChromaDB Vector Database
            try:
                chroma_name = rag_engine.index_document(doc.id, chunks)
                doc.chroma_collection_name = chroma_name
                db.commit()
            except Exception as ce:
                print(f"[ChromaDB] Indexing notice: {ce}")

            # 7. Store vectors in Supabase pgvector if configured
            if supabase_service.is_configured():
                try:
                    supabase_service.insert_document_chunks(supabase_chunks_payload)
                except Exception as se:
                    print(f"[Supabase pgvector] Notice: {se}")

            # 8. Generate comprehensive 7-part summary via Central Gemini Service
            summary_info = gemini_service.generate_comprehensive_summary(pages_data, original_filename)
            summary_info["chapters_outline"] = chapters

            doc.chunk_count = len(chunks)
            doc.summary = summary_info.get("executive_summary") or summary_info.get("short_summary", "")
            doc.key_points_json = json.dumps(summary_info)
            doc.status = "completed"
            db.commit()

            # Also persist in dedicated summaries table in Supabase
            db_summary = Summary(
                document_id=doc.id,
                user_id=current_user.id,
                executive_summary=doc.summary,
                key_concepts_json=doc.key_points_json
            )
            db.add(db_summary)

            # 8. Log activity in real-time timeline
            log = ActivityLog(
                user_id=current_user.id,
                activity_type="upload",
                title=f"Uploaded '{original_filename}'",
                description=f"Indexed {total_pages} pages into {len(chunks)} pgvector chunks via Gemini."
            )
            db.add(log)
            db.commit()

            # Clean up local temporary file immediately so no disk files linger
            try:
                if temp_file_path.exists():
                    temp_file_path.unlink()
            except Exception:
                pass

            return doc

        except Exception as e:
            # Clean up temp file on failure as well
            try:
                if temp_file_path.exists():
                    temp_file_path.unlink()
            except Exception:
                pass

            doc.status = "failed"
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error indexing document: {str(e)}")

    @staticmethod
    def get_user_documents(db: Session, user_id: int) -> List[Document]:
        return db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).all()

    @staticmethod
    def get_document_by_id(db: Session, doc_id: int, user_id: int) -> Optional[Document]:
        return db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()

    @staticmethod
    def delete_document(db: Session, doc_id: int, user_id: int) -> bool:
        doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == user_id).first()
        if not doc:
            return False

        # Remove from Supabase Storage
        if doc.storage_path:
            supabase_service.delete_pdf_from_storage(doc.storage_path)

        # Clean up any lingering temp file
        try:
            if doc.file_path and Path(doc.file_path).exists():
                Path(doc.file_path).unlink()
        except Exception:
            pass

        db.delete(doc)
        db.commit()
        return True
