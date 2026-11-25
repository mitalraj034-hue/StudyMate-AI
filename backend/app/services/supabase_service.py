import os
import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger("studymate.supabase")

class SupabaseService:
    """
    Centralized Supabase Cloud Service for StudyMate AI.
    Handles:
      1. Supabase Storage bucket uploads & deletions for Course PDFs
      2. pgvector semantic similarity search via match_document_chunks RPC
      3. Remote database synchronization with Supabase Cloud
    """

    def __init__(self):
        self.supabase_url = (
            getattr(settings, "SUPABASE_URL", "") or os.getenv("SUPABASE_URL", "")
        ).rstrip("/")
        self.service_role_key = (
            getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        self.anon_key = (
            getattr(settings, "SUPABASE_ANON_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")
        )
        self.bucket_name = (
            getattr(settings, "SUPABASE_STORAGE_BUCKET", "documents") or "documents"
        )
        self.timeout = 30.0

    def is_configured(self) -> bool:
        """Returns True if valid Supabase Cloud URL and credentials are set."""
        return bool(self.supabase_url and (self.service_role_key or self.anon_key))

    def _get_headers(self, use_service_role: bool = True) -> Dict[str, str]:
        key = self.service_role_key if (use_service_role and self.service_role_key) else (self.anon_key or self.service_role_key)
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    # =========================================================================
    # 1. SUPABASE STORAGE (BUCKET: 'documents')
    # =========================================================================
    def upload_pdf_to_storage(
        self,
        file_path_in_bucket: str,
        file_bytes: bytes,
        content_type: str = "application/pdf"
    ) -> str:
        """
        Uploads a PDF directly to Supabase Cloud Storage.
        Returns the remote storage path reference.
        """
        if not self.is_configured():
            logger.info("Supabase credentials not configured; document stored in memory/session.")
            return f"local://{file_path_in_bucket}"

        clean_path = file_path_in_bucket.lstrip("/")
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{clean_path}"
        headers = {
            "apikey": self.service_role_key or self.anon_key,
            "Authorization": f"Bearer {self.service_role_key or self.anon_key}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, content=file_bytes)
                if res.status_code in (200, 201):
                    logger.info(f"Successfully uploaded {clean_path} to Supabase Storage bucket '{self.bucket_name}'")
                    return f"{self.bucket_name}/{clean_path}"
                else:
                    logger.warning(f"Supabase Storage upload warning (Status {res.status_code}): {res.text}")
                    return f"{self.bucket_name}/{clean_path}"
        except Exception as e:
            logger.error(f"Failed to upload PDF to Supabase Storage: {e}")
            return f"{self.bucket_name}/{clean_path}"

    def download_pdf_from_storage(self, storage_path: str) -> Optional[bytes]:
        """Downloads PDF binary from Supabase Cloud Storage."""
        if not self.is_configured() or storage_path.startswith("local://"):
            return None

        clean_path = storage_path.replace(f"{self.bucket_name}/", "").lstrip("/")
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{clean_path}"
        headers = self._get_headers()

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, headers=headers)
                if res.status_code == 200:
                    return res.content
        except Exception as e:
            logger.error(f"Failed to download from Supabase Storage: {e}")
        return None

    def delete_pdf_from_storage(self, storage_path: str) -> bool:
        """Deletes PDF from Supabase Cloud Storage."""
        if not self.is_configured() or storage_path.startswith("local://"):
            return True

        clean_path = storage_path.replace(f"{self.bucket_name}/", "").lstrip("/")
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{clean_path}"
        headers = self._get_headers()

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.delete(url, headers=headers)
                return res.status_code in (200, 204)
        except Exception as e:
            logger.error(f"Failed to delete from Supabase Storage: {e}")
            return False

    # =========================================================================
    # 2. PGVECTOR SEMANTIC SIMILARITY SEARCH (RPC)
    # =========================================================================
    def search_vector_chunks(
        self,
        document_id: int,
        query_embedding: List[float],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Executes pgvector cosine similarity search using match_document_chunks RPC.
        """
        if not self.is_configured():
            return []

        url = f"{self.supabase_url}/rest/v1/rpc/match_document_chunks"
        headers = self._get_headers()
        payload = {
            "query_embedding": query_embedding,
            "filter_document_id": document_id,
            "match_count": top_k
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    results = res.json()
                    if isinstance(results, list):
                        return results
        except Exception as e:
            logger.warning(f"Supabase pgvector RPC search failed: {e}")
        return []

    # =========================================================================
    # 3. DIRECT INSERT OF CHUNKS WITH EMBEDDINGS
    # =========================================================================
    def insert_document_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Inserts text chunks with dense vector embeddings into Supabase document_chunks."""
        if not self.is_configured() or not chunks:
            return False

        url = f"{self.supabase_url}/rest/v1/document_chunks"
        headers = self._get_headers()
        headers["Prefer"] = "return=minimal"

        payload = []
        for c in chunks:
            payload.append({
                "document_id": c["document_id"],
                "chunk_index": c["chunk_index"],
                "page_number": c["page_number"],
                "content": c["content"],
                "embedding": c.get("embedding"),
                "metadata": c.get("metadata", {})
            })

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, json=payload)
                return res.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"Supabase REST chunk insert failed: {e}")
            return False

# Singleton Instance
supabase_service = SupabaseService()
