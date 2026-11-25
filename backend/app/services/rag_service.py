import json
import math
import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.document import Document
from app.models.chat_history import ChatHistory
from app.models.quiz_result import QuizResult
from app.models.flashcard import Flashcard
from app.models.extra import (
    DocumentChunk,
    Quiz,
    QuizAttempt,
    QuizAnswer,
    ChatMessage,
    ActivityLog,
    FlashcardSet,
    FlashcardProgress,
    Summary
)
from app.models.user import User
from app.services.gemini_service import gemini_service
from app.services.supabase_service import supabase_service
from rag_engine import RAGEngine

logger = logging.getLogger("studymate.rag")
rag_engine = RAGEngine()


class RAGService:
    """
    Orchestrates Grounded AI Chat, Comprehensive Summaries, Dynamic Quizzes,
    and Active Recall Flashcards using the Central Gemini AI Engine,
    ChromaDB vector search, and Supabase PostgreSQL persistence.
    """

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates cosine similarity between two dense embedding vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    @classmethod
    def retrieve_relevant_chunks(
        cls,
        db: Session,
        document_id: int,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k semantically relevant chunks with exact page citations.
        Uses ChromaDB vector search as primary, with fallback to pgvector / relational cosine search.
        """
        # 1. Primary: ChromaDB Vector Retrieval
        try:
            chroma_chunks = rag_engine.retrieve_context(doc_id=document_id, query=query, top_k=top_k)
            if chroma_chunks and len(chroma_chunks) > 0:
                return chroma_chunks
        except Exception as ce:
            logger.warning(f"ChromaDB retrieval notice: {ce}")

        # 2. Secondary: Supabase pgvector RPC
        query_emb = gemini_service.generate_embedding(query)
        if supabase_service.is_configured():
            try:
                remote_chunks = supabase_service.search_vector_chunks(
                    document_id=document_id,
                    query_embedding=query_emb,
                    top_k=top_k
                )
                if remote_chunks and len(remote_chunks) > 0:
                    return remote_chunks
            except Exception as se:
                logger.warning(f"Supabase pgvector search notice: {se}")

        # 3. Fallback: Query relational DocumentChunks with cosine similarity
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        if not chunks:
            return []

        scored_chunks = []
        for c in chunks:
            similarity = 0.6
            if c.embedding_json:
                try:
                    c_emb = json.loads(c.embedding_json)
                    sim = cls._cosine_similarity(query_emb, c_emb)
                    similarity = max(0.0, min(1.0, (sim + 1.0) / 2.0))
                except Exception:
                    pass
            scored_chunks.append({
                "id": c.id,
                "document_id": c.document_id,
                "chunk_index": c.chunk_index,
                "page_number": c.page_number,
                "content": c.content,
                "similarity": similarity,
                "relevance_score": int(similarity * 100)
            })

        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]

    @classmethod
    async def process_chat(
        cls,
        db: Session,
        current_user: User,
        document_id: int,
        query: str,
        custom_api_key: Optional[str] = None,
        mode: str = "Detailed Explanation",
        level: str = "Intermediate",
        language: str = "English",
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes AI Chat with Google Gemini:
        1. Validates document ownership.
        2. Retrieves relevant chunks via ChromaDB (chapter-aware).
        3. Retrieves conversation history for follow-up questions.
        4. Calls Gemini to generate the structured grounded tutor answer.
        5. Persists question, answer, and citations in Supabase.
        """
        doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found or access denied.")

        cleaned_query = query.strip()
        if not cleaned_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")

        # 1. Retrieve recent conversation history first for multi-turn context
        history_rows = db.query(ChatHistory).filter(
            ChatHistory.document_id == doc.id,
            ChatHistory.user_id == current_user.id
        ).order_by(ChatHistory.created_at.asc()).all()

        conv_history = []
        for h in history_rows[-8:]:
            conv_history.append({"role": "user", "content": h.question})
            conv_history.append({"role": "assistant", "content": h.answer})

        # 2. Formulate intelligent retrieval query with pronoun and follow-up expansion
        retrieval_query = cleaned_query
        if history_rows:
            last_q = history_rows[-1].question.strip()
            # Clean last query of question prefixes to isolate core topic
            subject = re.sub(r'^(what is|what are|explain|describe|tell me about|how does|why is|define|discuss)\s+', '', last_q, flags=re.IGNORECASE).strip(' ?.')
            words = set(re.findall(r'\b\w+\b', cleaned_query.lower()))
            follow_up_cues = {"it", "its", "this", "that", "these", "those", "them", "they", "types", "example", "examples", "more", "shorter", "again", "understand", "hinglish", "hindi", "question", "quiz", "difference", "compare", "step", "steps"}
            if words.intersection(follow_up_cues) or len(cleaned_query.split()) <= 4:
                # If query doesn't already contain the subject, blend it for semantic retrieval
                if subject and subject.lower() not in cleaned_query.lower():
                    retrieval_query = f"{subject} {cleaned_query}"

        # 3. Retrieve relevant chunks using ChromaDB / pgvector
        retrieved_chunks = cls.retrieve_relevant_chunks(db, doc.id, retrieval_query, top_k=8)

        # 4. Generate grounded answer via Central Gemini Service with tutor mode & level
        rag_result = gemini_service.generate_chat_answer(
            query=cleaned_query,
            retrieved_chunks=retrieved_chunks,
            document_title=doc.original_filename,
            conversation_history=conv_history,
            mode=mode,
            level=level,
            language=language,
            action=action
        )

        citations = rag_result.get("citations", [])
        citations_json = json.dumps(citations)

        # 4. Persist in ChatHistory table in Supabase PostgreSQL
        chat_entry = ChatHistory(
            user_id=current_user.id,
            document_id=doc.id,
            question=cleaned_query,
            answer=rag_result["answer"],
            citations=citations_json
        )
        db.add(chat_entry)

        # 5. Persist ChatMessage records
        user_msg = ChatMessage(
            document_id=doc.id,
            user_id=current_user.id,
            role="user",
            content=cleaned_query
        )
        bot_msg = ChatMessage(
            document_id=doc.id,
            user_id=current_user.id,
            role="assistant",
            content=rag_result["answer"],
            citations_json=citations_json
        )
        db.add(user_msg)
        db.add(bot_msg)

        # 6. Activity Log
        log = ActivityLog(
            user_id=current_user.id,
            activity_type="chat",
            title=f"Asked: '{cleaned_query[:40]}...'",
            description=f"Synthesized by Gemini ({mode}, {level}) with {len(citations)} citation(s)."
        )
        db.add(log)
        db.commit()

        return {
            "answer": rag_result["answer"],
            "citations": citations,
            "confidence": rag_result.get("confidence", 94),
            "grounded": rag_result.get("grounded", True),
            "chat_history_id": chat_entry.id,
            "message_id": bot_msg.id,
            "mode": rag_result.get("mode", mode),
            "level": rag_result.get("level", level),
            "language": rag_result.get("language", language),
            "follow_up_suggestions": rag_result.get("follow_up_suggestions", [])
        }

    @staticmethod
    def get_document_chat_history(db: Session, current_user: User, document_id: int) -> List[Dict[str, Any]]:
        """Returns ordered chat turns for the specified document."""
        doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found or access denied.")

        history_rows = db.query(ChatHistory).filter(
            ChatHistory.document_id == document_id,
            ChatHistory.user_id == current_user.id
        ).order_by(ChatHistory.created_at.asc()).all()

        results = []
        for h in history_rows:
            citations_list = json.loads(h.citations) if h.citations else []
            results.append({
                "id": h.id,
                "user_id": h.user_id,
                "document_id": h.document_id,
                "question": h.question,
                "answer": h.answer,
                "citations": citations_list,
                "created_at": h.created_at.isoformat()
            })
        return results

    @staticmethod
    def clear_document_chat_history(db: Session, current_user: User, document_id: int) -> Dict[str, Any]:
        """Clears all conversation history for the student and document in Supabase."""
        doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found or access denied.")

        db.query(ChatHistory).filter(
            ChatHistory.document_id == document_id,
            ChatHistory.user_id == current_user.id
        ).delete()

        db.query(ChatMessage).filter(
            ChatMessage.document_id == document_id,
            ChatMessage.user_id == current_user.id
        ).delete()

        db.commit()
        return {"message": "Chat history cleared successfully."}

    @staticmethod
    def generate_summary_for_doc(
        db: Session,
        current_user: User,
        document_id: int,
        summary_type: str = "Detailed Summary",
        length: str = "Detailed",
        topic: Optional[str] = None,
        level: str = "Intermediate",
        language: str = "English",
        action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates advanced academic summaries (Quick, Detailed, Chapter-wise, Exam Notes,
        Last-Minute Revision, Topic-wise) using Google Gemini and persists to Supabase.
        """
        doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found or access denied.")

        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index.asc()).all()
        if not chunks:
            raise HTTPException(status_code=400, detail="Document has no processed content.")

        pages_dict = {}
        for c in chunks:
            pages_dict.setdefault(c.page_number, []).append(c.content)

        pages_data = [{"page_number": p, "text": " ".join(texts)} for p, texts in sorted(pages_dict.items())]

        # Call Gemini to generate the customized academic summary
        summary_result = gemini_service.generate_advanced_summary(
            pages_data=pages_data,
            document_title=doc.original_filename,
            summary_type=summary_type,
            length=length,
            topic=topic,
            level=level,
            language=language,
            action=action
        )

        doc.summary = summary_result.get("short_summary") or summary_result.get("executive_summary", "")
        doc.key_points_json = json.dumps(summary_result)
        db.commit()

        # Save to Summary table
        db_summary = Summary(
            document_id=doc.id,
            user_id=current_user.id,
            executive_summary=doc.summary,
            key_concepts_json=doc.key_points_json
        )
        db.add(db_summary)
        db.commit()

        return summary_result

    @staticmethod
    def generate_quiz_for_doc(
        db: Session,
        current_user: User,
        document_id: int,
        count: int = 5,
        difficulty: str = "Medium",
        title: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gemini dynamically generates all quiz questions from the PDF.
        Persists quiz questions, options, and explanations into Supabase PostgreSQL.
        """
        doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found or access denied.")

        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        if not chunks:
            raise HTTPException(status_code=400, detail="Document has no processed content.")

        chunk_dicts = [{"chunk_index": c.chunk_index, "page_number": c.page_number, "content": c.content} for c in chunks]

        # Google Gemini dynamically generates questions
        questions = gemini_service.generate_dynamic_quiz(
            chunks=chunk_dicts,
            count=count,
            difficulty=difficulty,
            topic=topic,
            document_title=doc.original_filename
        )

        quiz_title = title or f"{difficulty} Quiz: {doc.original_filename} ({len(questions)} Questions)"
        new_quiz = Quiz(
            document_id=doc.id,
            user_id=current_user.id,
            title=quiz_title,
            topic=topic or "General Syllabus",
            difficulty=difficulty,
            total_questions=len(questions),
            questions_json=json.dumps(questions)
        )
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)

        log = ActivityLog(
            user_id=current_user.id,
            activity_type="quiz",
            title=f"Generated Quiz: '{quiz_title}'",
            description=f"Created {len(questions)} questions via Google Gemini."
        )
        db.add(log)
        db.commit()

        return {
            "id": new_quiz.id,
            "document_id": doc.id,
            "title": new_quiz.title,
            "difficulty": new_quiz.difficulty,
            "total_questions": new_quiz.total_questions,
            "questions": questions
        }

    @staticmethod
    def submit_quiz_attempt(
        db: Session,
        current_user: User,
        quiz_id: int,
        answers: Dict[str, int],
        time_spent_seconds: int = 60
    ) -> Dict[str, Any]:
        """Evaluates quiz attempt and saves results in Supabase."""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.user_id == current_user.id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found.")

        questions = json.loads(quiz.questions_json)
        correct_count = 0
        feedback = []

        for q in questions:
            q_id_str = str(q["id"])
            user_choice = answers.get(q_id_str)
            correct_idx = q.get("correct_answer_index", q.get("correct_index", 0))
            is_correct = (user_choice == correct_idx)
            if is_correct:
                correct_count += 1

            feedback.append({
                "id": q["id"],
                "question": q["question"],
                "user_choice": user_choice,
                "correct_index": correct_idx,
                "is_correct": is_correct,
                "explanation": q.get("explanation", ""),
                "page_number": q.get("page_number", 1)
            })

        total = len(questions)
        wrong_count = max(0, total - correct_count)
        percentage = round((correct_count / total * 100) if total > 0 else 0, 1)

        # 1. Save in QuizResults table
        quiz_result = QuizResult(
            user_id=current_user.id,
            document_id=quiz.document_id,
            total_questions=total,
            correct_answers=correct_count,
            wrong_answers=wrong_count,
            score=correct_count,
            percentage=percentage
        )
        db.add(quiz_result)

        # 2. Save in QuizAttempt table
        attempt = QuizAttempt(
            quiz_id=quiz.id,
            document_id=quiz.document_id,
            user_id=current_user.id,
            score=correct_count,
            total_questions=total,
            percentage=percentage,
            answers_json=json.dumps(answers),
            time_spent_seconds=time_spent_seconds
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        # 3. Save individual answers in quiz_answers table
        for fb in feedback:
            ans_record = QuizAnswer(
                attempt_id=attempt.id,
                question_index=fb.get("id"),
                user_choice=fb.get("user_choice"),
                is_correct=fb.get("is_correct", False)
            )
            db.add(ans_record)

        # 4. Activity Log
        log = ActivityLog(
            user_id=current_user.id,
            activity_type="quiz",
            title=f"Completed Quiz: {percentage}%",
            description=f"Scored {correct_count}/{total} in '{quiz.title}'."
        )
        db.add(log)
        db.commit()

        return {
            "result_id": quiz_result.id,
            "attempt_id": attempt.id,
            "score": correct_count,
            "total_questions": total,
            "correct_answers": correct_count,
            "wrong_answers": wrong_count,
            "percentage": percentage,
            "feedback": feedback
        }

    @staticmethod
    def generate_flashcards_for_doc(
        db: Session,
        current_user: User,
        document_id: int,
        count: int = 8,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Gemini dynamically generates flashcards from the PDF."""
        doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        if not chunks:
            raise HTTPException(status_code=400, detail="Document has no processed content.")

        chunk_dicts = [{"chunk_index": c.chunk_index, "page_number": c.page_number, "content": c.content} for c in chunks]

        # Google Gemini dynamically generates flashcards from PDF
        generated_cards = gemini_service.generate_dynamic_flashcards(
            chunks=chunk_dicts,
            count=count,
            topic=topic,
            document_title=doc.original_filename
        )

        # Create FlashcardSet
        fc_set = FlashcardSet(
            document_id=doc.id,
            user_id=current_user.id,
            title=f"Flashcards: {doc.original_filename}",
            total_cards=len(generated_cards)
        )
        db.add(fc_set)
        db.commit()
        db.refresh(fc_set)

        cards_out = []
        for fc in generated_cards:
            card = Flashcard(
                document_id=doc.id,
                user_id=current_user.id,
                question=fc["front"],
                answer=fc["back"],
                status="new",
                topic=fc.get("topic", "Key Concept"),
                page_number=fc.get("page_number", 1)
            )
            db.add(card)
            db.commit()
            db.refresh(card)

            prog = FlashcardProgress(
                user_id=current_user.id,
                flashcard_id=card.id,
                mastery_status="new",
                review_count=0
            )
            db.add(prog)
            cards_out.append(card)

        log = ActivityLog(
            user_id=current_user.id,
            activity_type="flashcard",
            title=f"Generated {len(cards_out)} Flashcards",
            description=f"Created active-recall study deck for '{doc.original_filename}' via Google Gemini."
        )
        db.add(log)
        db.commit()

        return [
            {
                "id": c.id,
                "document_id": c.document_id,
                "question": c.question,
                "answer": c.answer,
                "front": c.question,
                "back": c.answer,
                "status": c.status,
                "mastery_status": c.mastery_status,
                "topic": c.topic,
                "page_number": c.page_number,
                "created_at": c.created_at.isoformat()
            }
            for c in cards_out
        ]
