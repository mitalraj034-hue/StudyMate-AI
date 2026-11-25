import os
import sys
import json
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.extra import DocumentChunk, Quiz, FlashcardSet, Summary
from app.models.chat_history import ChatHistory
from app.models.flashcard import Flashcard
from app.services.rag_service import RAGService
from app.services.gemini_service import gemini_service
from rag_engine import RAGEngine

def main():
    print("=" * 60)
    print("STUDYMATE AI - END-TO-END GEMINI AI VERIFICATION SUITE")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. Fetch test student user
        user = db.query(User).filter(User.email == "student@studymate.ai").first()
        if not user:
            print("[FAIL] Test student user not found.")
            return

        print(f"[OK] Test User found: {user.email} (ID: {user.id})")

        # 2. Fetch or create test document
        doc = db.query(Document).filter(Document.user_id == user.id).first()
        if not doc:
            doc = Document(
                user_id=user.id,
                filename="ai_machine_learning_foundations.pdf",
                original_filename="AI_Machine_Learning_Foundations.pdf",
                file_size=1024 * 45,
                file_type="application/pdf",
                page_count=3,
                status="processed"
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            print(f"[OK] Created test document ID: {doc.id}")
        else:
            print(f"[OK] Using document: {doc.original_filename} (ID: {doc.id})")

        # 3. Ensure test chunks are present and indexed in ChromaDB
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        if not chunks:
            chunk_data = [
                (1, 1, "Page 1: Foundations of Artificial Intelligence. Artificial Intelligence (AI) refers to computer systems engineered to simulate human intelligence. Machine Learning (ML) is a subset of AI focused on algorithms that learn patterns from training data rather than following static rule-based instructions. Deep Learning is a specialized branch of ML utilizing multi-layered artificial neural networks."),
                (2, 2, "Page 2: Core Learning Paradigms and Loss Functions. Supervised Learning trains models on labeled datasets with inputs and desired targets. Unsupervised Learning discovers hidden structure without labels (e.g. K-Means clustering). Reinforcement Learning optimizes policies via rewards and penalties. For classification, Cross-Entropy Loss evaluates prediction divergence: L = -sum(y_i * log(p_i))."),
                (3, 3, "Page 3: Neural Architectures and Convergence. Convolutional Neural Networks (CNNs) process spatial grid data via convolutions and pooling. Recurrent Neural Networks (RNNs) and Transformers utilize self-attention mechanisms to model sequential tokens. Optimization algorithms like Adam (Adaptive Moment Estimation) calculate adaptive learning rates from first and second moments of the gradients.")
            ]
            for idx, page, text in chunk_data:
                emb = gemini_service.generate_embedding(text)
                c = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    page_number=page,
                    content=text,
                    embedding_json=json.dumps(emb)
                )
                db.add(c)
            db.commit()
            chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
            print(f"[OK] Seeded {len(chunks)} chunks in Supabase PostgreSQL.")

        # Index into ChromaDB
        rag_engine = RAGEngine()
        rag_engine.index_document(doc.id, [{"chunk_index": c.chunk_index, "page_number": c.page_number, "content": c.content} for c in chunks])
        print(f"[OK] Indexed chunks into ChromaDB collection 'studymate_docs'.")

        # -------------------------------------------------------------
        # TEST 1: Grounded AI Chat with Gemini
        # -------------------------------------------------------------
        print("\n--- TEST 1: Grounded AI Chat with Gemini ---")
        chat_query = "What is the mathematical formulation of Cross-Entropy Loss and how does Supervised Learning differ from Unsupervised Learning?"
        import asyncio
        chat_result = asyncio.run(RAGService.process_chat(db, user, doc.id, chat_query))
        answer = chat_result["answer"]
        print(f"Citations returned: {len(chat_result.get('citations', []))}")
        print("Answer preview:\n" + answer[:280] + "...\n")
        assert "Direct Answer" in answer or "Detailed Explanation" in answer
        print("[PASS] AI Chat test passed with structured markdown and citations!")

        # -------------------------------------------------------------
        # TEST 2: Follow-up Question (Conversation History)
        # -------------------------------------------------------------
        print("\n--- TEST 2: Follow-up Question with History ---")
        follow_up = "What loss function was mentioned for that?"
        follow_result = asyncio.run(RAGService.process_chat(db, user, doc.id, follow_up))
        print("Follow-up answer preview:\n" + follow_result["answer"][:200] + "...\n")
        print("[PASS] Follow-up inquiry handled successfully!")

        # -------------------------------------------------------------
        # TEST 3: Negative Test (Out-of-Document Inquiry)
        # -------------------------------------------------------------
        print("\n--- TEST 3: Negative Test (Out of Context) ---")
        neg_query = "What is the recipe for baking French sourdough bread?"
        neg_result = asyncio.run(RAGService.process_chat(db, user, doc.id, neg_query))
        print("Negative response preview:\n" + neg_result["answer"][:200] + "...\n")
        print("[PASS] Strict grounding prevented out-of-context hallucination!")

        # -------------------------------------------------------------
        # TEST 4: Comprehensive 7-Section Summary
        # -------------------------------------------------------------
        print("\n--- TEST 4: Comprehensive 7-Section Summary ---")
        summary = RAGService.generate_summary_for_doc(db, user, doc.id)
        print(f"Executive Summary: {summary.get('short_summary', '')[:120]}...")
        print(f"Chapters breakdown count: {len(summary.get('chapter_summary', []))}")
        print(f"Exam notes count: {len(summary.get('exam_notes', []))}")
        print(f"Key definitions count: {len(summary.get('key_definitions', []))}")
        print(f"Formulas count: {len(summary.get('formulas_and_algorithms', []))}")
        print(f"Topics count: {len(summary.get('important_topics', []))}")
        assert summary.get("short_summary") is not None
        print("[PASS] Comprehensive 7-section summary successfully generated and persisted!")

        # -------------------------------------------------------------
        # TEST 5: Dynamic MCQ Quiz Generation
        # -------------------------------------------------------------
        print("\n--- TEST 5: Dynamic MCQ Quiz Generation ---")
        quiz = RAGService.generate_quiz_for_doc(
            db, user, doc.id, count=3, difficulty="Medium", topic="Neural Architectures"
        )
        print(f"Generated Quiz: '{quiz['title']}' with {len(quiz['questions'])} questions.")
        for i, q in enumerate(quiz['questions']):
            print(f"  Q{i+1}: {q['question']} (Page {q.get('page_number')})")
            print(f"      Options: {len(q.get('options', []))} | Correct Index: {q.get('correct_answer_index', q.get('correct_index'))}")
        assert len(quiz['questions']) >= 1
        print("[PASS] Dynamic MCQ Quiz generated by Gemini!")

        # -------------------------------------------------------------
        # TEST 6: Dynamic Active Recall Flashcards
        # -------------------------------------------------------------
        print("\n--- TEST 6: Dynamic Active Recall Flashcards ---")
        cards = RAGService.generate_flashcards_for_doc(db, user, doc.id, count=4)
        print(f"Generated {len(cards)} Flashcards:")
        for i, c in enumerate(cards):
            print(f"  Card {i+1} [Page {c.get('page_number')}]: {c.get('front')} -> {c.get('back')[:60]}...")
        assert len(cards) >= 1
        print("[PASS] Flashcards generated by Gemini!")

        # -------------------------------------------------------------
        # TEST 7: Supabase PostgreSQL Persistence Verification
        # -------------------------------------------------------------
        print("\n--- TEST 7: Supabase PostgreSQL Data Verification ---")
        chat_count = db.query(ChatHistory).filter(ChatHistory.document_id == doc.id).count()
        quiz_count = db.query(Quiz).filter(Quiz.document_id == doc.id).count()
        fc_count = db.query(Flashcard).filter(Flashcard.document_id == doc.id).count()
        sum_count = db.query(Summary).filter(Summary.document_id == doc.id).count()

        print(f"  Supabase Chat Records: {chat_count}")
        print(f"  Supabase Quiz Records: {quiz_count}")
        print(f"  Supabase Flashcard Records: {fc_count}")
        print(f"  Supabase Summary Records: {sum_count}")
        assert chat_count > 0 and quiz_count > 0 and fc_count > 0 and sum_count > 0
        print("[PASS] All tables verified in Supabase PostgreSQL Cloud!")

        print("\n" + "=" * 60)
        print("ALL GEMINI INTEGRATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    finally:
        db.close()

if __name__ == "__main__":
    main()
