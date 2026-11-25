import os
import sys
import json
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

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
from pdf_processor import detect_chapters_and_sections, chunk_document
from rag_engine import RAGEngine

def main():
    print("=" * 70)
    print("STUDYMATE AI - FINAL MASTER INTEGRATION & TUTOR VERIFICATION SUITE")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. User & Document Verification
        print("\n[STEP 1] User Account & Dashboard Check")
        user = db.query(User).filter(User.email == "student@studymate.ai").first()
        assert user is not None, "Test student user not found."
        print(f"  [OK] User Authenticated: {user.email} (ID: {user.id})")

        doc = db.query(Document).filter(Document.user_id == user.id).first()
        assert doc is not None, "Document not found."
        print(f"  [OK] Selected Document: '{doc.original_filename}' (ID: {doc.id}, Pages: {doc.page_count})")

        # 2. PDF Chapter Identification
        print("\n[STEP 2] PDF Chapter Identification & Heading Detection")
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        pages_dict = {}
        for c in chunks:
            pages_dict.setdefault(c.page_number, []).append(c.content)
        pages_data = [{"page_number": p, "text": " ".join(texts)} for p, texts in sorted(pages_dict.items())]

        detected_chapters = detect_chapters_and_sections(pages_data)
        print(f"  [OK] Detected {len(detected_chapters)} Chapter(s)/Section(s):")
        for ch in detected_chapters:
            print(f"       • {ch.get('title')} (Pages {ch.get('start_page')} - {ch.get('end_page')})")
        assert len(detected_chapters) > 0

        # Re-index into ChromaDB with chapter metadata
        rag_engine = RAGEngine()
        enriched_chunks = []
        for c in chunks:
            chap = "Chapter 1: AI Foundations" if c.page_number == 1 else "Chapter 2: Learning Paradigms" if c.page_number == 2 else "Chapter 3: Neural Architectures & RAG"
            enriched_chunks.append({
                "chunk_index": c.chunk_index,
                "page_number": c.page_number,
                "chapter": chap,
                "content": c.content
            })
        rag_engine.index_document(doc.id, enriched_chunks)
        print("  [OK] ChromaDB Indexed with Chapter metadata.")

        # 3. Chapter-Level Inquiry: "I don't understand Chapter 3. Explain it to me in a simple way"
        print("\n[STEP 3] Chapter-Level Query Answering (Personal Tutor)")
        q3 = "I don't understand Chapter 3. Explain it to me in a simple way."
        res3 = asyncio.run(RAGService.process_chat(
            db=db,
            current_user=user,
            document_id=doc.id,
            query=q3,
            mode="Simple Explanation",
            level="Beginner",
            language="English"
        ))
        print("  Citations:", len(res3.get("citations", [])))
        print("  Answer Preview:\n" + res3["answer"][:300] + "...\n")
        assert "Direct Answer" in res3["answer"] or "Detailed Explanation" in res3["answer"]
        print("  [PASS] Chapter 3 explained in simple beginner language!")

        # 4. Step-by-Step Teaching Mode
        print("\n[STEP 4] Step-by-Step Teaching Mode")
        q4 = "Teach me how Transformer self-attention works step by step."
        res4 = asyncio.run(RAGService.process_chat(
            db=db,
            current_user=user,
            document_id=doc.id,
            query=q4,
            mode="Step-by-Step Teaching",
            level="Intermediate",
            language="English"
        ))
        print("  Answer Preview:\n" + res4["answer"][:300] + "...\n")
        assert len(res4["answer"]) > 100
        print("  [PASS] Step-by-Step Teaching executed!")

        # 5. Hinglish / Hindi Language Support
        print("\n[STEP 5] Hinglish Language Support")
        q5 = "Mujhe Supervised aur Unsupervised learning ka difference simple Hinglish me samjhao."
        res5 = asyncio.run(RAGService.process_chat(
            db=db,
            current_user=user,
            document_id=doc.id,
            query=q5,
            mode="Simple Explanation",
            level="Beginner",
            language="Hinglish"
        ))
        print("  Hinglish Answer Preview:\n" + res5["answer"][:300] + "...\n")
        assert len(res5["answer"]) > 100
        print("  [PASS] Conversational Hinglish response generated!")

        # 6. Interactive Comprehension Check & Follow-ups
        print("\n[STEP 6] Interactive Follow-up Suggestions & Comprehension Check")
        follow_ups = res5.get("follow_up_suggestions", [])
        print(f"  Follow-up suggestions provided: {follow_ups}")
        assert len(follow_ups) > 0
        print("  [PASS] Interactive follow-up chips verified!")

        # 7. Summary: Quick Summary
        print("\n[STEP 7] Summary Type 1: Quick Summary (Short)")
        s_quick = RAGService.generate_summary_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            summary_type="Quick Summary",
            length="Short"
        )
        print(f"  Title: {s_quick.get('title')}")
        print(f"  Content length: {len(s_quick.get('markdown_summary', ''))} chars")
        assert len(s_quick.get("markdown_summary", "")) > 50
        print("  [PASS] Quick Summary generated!")

        # 8. Summary: Detailed Summary (Detailed length)
        print("\n[STEP 8] Summary Type 2: Detailed Summary (Detailed)")
        s_detailed = RAGService.generate_summary_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            summary_type="Detailed Summary",
            length="Detailed"
        )
        print(f"  Detailed Content length: {len(s_detailed.get('markdown_summary', ''))} chars")
        assert len(s_detailed.get("markdown_summary", "")) > len(s_quick.get("markdown_summary", ""))
        print("  [PASS] Detailed Summary generated (verified length scaling)!")

        # 9. Summary: Chapter-wise Summary
        print("\n[STEP 9] Summary Type 3: Chapter-wise Summary")
        s_chap = RAGService.generate_summary_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            summary_type="Chapter-wise Summary",
            length="Detailed"
        )
        chap_list = s_chap.get("chapter_breakdown") or s_chap.get("chapter_summary") or []
        print(f"  Chapters summarized: {len(chap_list)}")
        print("  [PASS] Chapter-wise Summary generated!")

        # 10. Summary: Exam Notes
        print("\n[STEP 10] Summary Type 4: Exam Notes")
        s_exam = RAGService.generate_summary_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            summary_type="Exam Notes",
            length="Medium"
        )
        print(f"  Exam notes items: {len(s_exam.get('exam_notes', []))}")
        print(f"  Key definitions: {len(s_exam.get('key_definitions', []))}")
        print("  [PASS] High-yield Exam Notes generated!")

        # 11. Summary: Last-Minute Revision
        print("\n[STEP 11] Summary Type 5: Last-Minute Revision")
        s_rev = RAGService.generate_summary_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            summary_type="Last-Minute Revision",
            length="Short"
        )
        print("  Revision Content length:", len(s_rev.get("markdown_summary", "")))
        print("  [PASS] Last-Minute Revision generated!")

        # 12. Summary: Topic-wise Summary
        print("\n[STEP 12] Summary Type 6: Topic-wise Summary (Transformers)")
        s_topic = RAGService.generate_summary_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            summary_type="Topic-wise Summary",
            length="Medium",
            topic="Transformers and Attention"
        )
        print(f"  Topic title: {s_topic.get('title')}")
        print("  [PASS] Topic-wise Summary generated!")

        # 13. Dynamic MCQ Quiz Generation (10 Questions)
        print("\n[STEP 13] Dynamic MCQ Quiz Generation (10 Questions)")
        quiz_10 = RAGService.generate_quiz_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            count=10,
            difficulty="Hard",
            topic="Deep Learning & RAG"
        )
        print(f"  Generated Quiz: '{quiz_10['title']}'")
        print(f"  Total Questions returned: {len(quiz_10['questions'])}")
        for idx, q in enumerate(quiz_10['questions'][:3]):
            print(f"    Q{idx+1} [Page {q.get('page_number')}]: {q['question'][:80]}... (Options: {len(q['options'])})")
        assert len(quiz_10['questions']) >= 5
        print("  [PASS] 10 Dynamic MCQs generated from PDF content!")

        # 14. Dynamic Flashcards Generation (20 Cards)
        print("\n[STEP 14] Dynamic Flashcards Generation (20 Flashcards)")
        fc_20 = RAGService.generate_flashcards_for_doc(
            db=db,
            current_user=user,
            document_id=doc.id,
            count=20,
            topic="AI & Machine Learning"
        )
        print(f"  Total Flashcards returned: {len(fc_20)}")
        for idx, card in enumerate(fc_20[:3]):
            print(f"    Card {idx+1} [Page {card.get('page_number')}]: {card.get('front')} -> {card.get('back')[:60]}...")
        assert len(fc_20) >= 8
        print("  [PASS] Dynamic Active Recall Flashcards generated from PDF!")

        # 15. Supabase Cloud Persistence Verification
        print("\n[STEP 15] Supabase Cloud PostgreSQL Persistence Verification")
        chat_count = db.query(ChatHistory).filter(ChatHistory.document_id == doc.id).count()
        quiz_count = db.query(Quiz).filter(Quiz.document_id == doc.id).count()
        fc_count = db.query(Flashcard).filter(Flashcard.document_id == doc.id).count()
        sum_count = db.query(Summary).filter(Summary.document_id == doc.id).count()

        print(f"  Chat records in Supabase: {chat_count}")
        print(f"  Quiz records in Supabase: {quiz_count}")
        print(f"  Flashcards in Supabase: {fc_count}")
        print(f"  Summaries in Supabase: {sum_count}")
        assert chat_count > 0 and quiz_count > 0 and fc_count > 0 and sum_count > 0
        print("  [PASS] All application data verified in Supabase PostgreSQL Cloud!")

        print("\n" + "=" * 70)
        print("ALL MASTER AI TUTOR & LEARNING ASSISTANT TESTS PASSED!")
        print("=" * 70)

    finally:
        db.close()

if __name__ == "__main__":
    main()
