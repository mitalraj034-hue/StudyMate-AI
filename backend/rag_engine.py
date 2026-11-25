import os
import re
import math
import json
import logging
from typing import List, Dict, Any, Optional
from collections import Counter
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from config import settings

logger = logging.getLogger("studymate.rag_engine")

class StudyMateEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, dimension: int = 128):
        super().__init__()
        self.dimension = dimension

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: List[List[float]] = []
        for text in input:
            tokens = re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', text.lower())
            vec = [0.0] * self.dimension
            if not tokens:
                embeddings.append(vec)
                continue
            
            token_counts = Counter(tokens)
            for token, count in token_counts.items():
                bucket = abs(hash(token)) % self.dimension
                sign = 1.0 if (hash(token + "_sign") % 2 == 0) else -1.0
                weight = (1.0 + math.log(count)) * sign
                vec[bucket] += weight

            norm = math.sqrt(sum(x * x for x in vec))
            if norm > 0:
                vec = [x / norm for x in vec]
            embeddings.append(vec)
        return embeddings


class RAGEngine:
    """
    Local ChromaDB Vector Search Engine for StudyMate AI.
    Provides fast, chapter-aware top-k semantic retrieval and provenance tracking.
    """

    def __init__(self):
        settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=str(settings.CHROMA_DIR))
        self.embedding_fn = StudyMateEmbeddingFunction(dimension=128)

    def get_collection_name(self, doc_id: int) -> str:
        return f"doc_collection_{doc_id}"

    def index_document(self, doc_id: int, chunks: List[Dict[str, Any]]) -> str:
        """Indexes document chunks into ChromaDB with page and chapter metadata."""
        collection_name = self.get_collection_name(doc_id)
        
        try:
            self.chroma_client.delete_collection(name=collection_name)
        except Exception:
            pass

        collection = self.chroma_client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

        if not chunks:
            return collection_name

        ids = [f"chk_{chunk.get('chunk_index', i)}" for i, chunk in enumerate(chunks)]
        documents = [chunk.get("content", "") for chunk in chunks]
        metadatas = [
            {
                "page_number": int(chunk.get("page_number", 1)),
                "chunk_index": int(chunk.get("chunk_index", i)),
                "chapter": str(chunk.get("chapter", "General Section"))
            }
            for i, chunk in enumerate(chunks)
        ]

        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.add(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )

        return collection_name

    def delete_document_index(self, doc_id: int):
        try:
            self.chroma_client.delete_collection(name=self.get_collection_name(doc_id))
        except Exception:
            pass

    def retrieve_context(self, doc_id: int, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        """
        Retrieves relevant chunks with page citations from ChromaDB.
        Intelligently detects chapter inquiries and retrieves all chunks from that chapter.
        """
        collection_name = self.get_collection_name(doc_id)
        try:
            collection = self.chroma_client.get_collection(
                name=collection_name, 
                embedding_function=self.embedding_fn
            )
        except Exception:
            return []

        count = collection.count()
        if count == 0:
            return []

        # 1. Check if user inquiry specifically asks for a Page number
        page_match = re.search(r'\b(?:page|pg|p\.?)\s*([0-9]+)\b', query, re.IGNORECASE)
        if page_match:
            try:
                target_page = int(page_match.group(1))
                all_data = collection.get(include=["documents", "metadatas"])
                if all_data and all_data.get("documents"):
                    page_chunks = []
                    for doc_text, meta in zip(all_data["documents"], all_data["metadatas"]):
                        p_num = meta.get("page_number")
                        if p_num is not None and int(p_num) == target_page:
                            page_chunks.append({
                                "page_number": target_page,
                                "chunk_index": meta.get("chunk_index", 0),
                                "chapter": meta.get("chapter", f"Page {target_page}"),
                                "content": doc_text,
                                "relevance_score": 99
                            })

                    if page_chunks:
                        page_chunks.sort(key=lambda x: x["chunk_index"])
                        return page_chunks[:10]
            except Exception as pe:
                logger.warning(f"Page-filtered retrieval notice: {pe}")

        # 2. Check if user inquiry specifically asks for a Chapter/Unit/Section
        chapter_match = re.search(r'\b(?:chapter|unit|module|section|ch)\s*([0-9IVXLCDM]+)\b', query, re.IGNORECASE)
        if chapter_match:
            chap_num = chapter_match.group(1).lower()
            try:
                # Retrieve all items in the collection and filter by chapter
                all_data = collection.get(include=["documents", "metadatas"])
                if all_data and all_data.get("documents"):
                    matching_chunks = []
                    for doc_text, meta in zip(all_data["documents"], all_data["metadatas"]):
                        chap_meta = str(meta.get("chapter", "")).lower()
                        if f"chapter {chap_num}" in chap_meta or f"unit {chap_num}" in chap_meta or f"module {chap_num}" in chap_meta:
                            matching_chunks.append({
                                "page_number": meta.get("page_number", 1),
                                "chunk_index": meta.get("chunk_index", 0),
                                "chapter": meta.get("chapter", "General Section"),
                                "content": doc_text,
                                "relevance_score": 96
                            })

                    if matching_chunks:
                        # Sort by chunk_index to present continuous reading flow
                        matching_chunks.sort(key=lambda x: x["chunk_index"])
                        return matching_chunks[:12] # return comprehensive chapter material
            except Exception as e:
                logger.warning(f"Chapter-filtered retrieval notice: {e}")

        # 3. Standard semantic vector similarity search
        actual_k = min(max(top_k, 6), count)
        results = collection.query(
            query_texts=[query],
            n_results=actual_k
        )

        retrieved: List[Dict[str, Any]] = []
        if results and results.get("documents") and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for d, m, dist in zip(docs, metas, distances):
                similarity = max(50, min(99, int((1.0 - (dist / 2.0)) * 100)))
                retrieved.append({
                    "page_number": m.get("page_number", 1),
                    "chunk_index": m.get("chunk_index", 0),
                    "chapter": m.get("chapter", "General Section"),
                    "content": d,
                    "relevance_score": similarity
                })

        return retrieved
