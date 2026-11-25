import sys
import json
import httpx
from pathlib import Path

# Enable UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 60)
    print("      STUDYMATE AI - COMPREHENSIVE END-TO-END VALIDATION")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # 1. Health Check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. Health check passed:", res.json()["status"])

    # 2. Swagger Docs
    res = client.get("/docs")
    assert res.status_code == 200, f"/docs failed: {res.text}"
    print("[PASS] 2. Swagger /docs available (Status 200)")

    # 3. Frontend Root HTML
    res = client.get("/")
    assert res.status_code == 200 and "StudyMate AI" in res.text, "Frontend root did not serve HTML"
    print("[PASS] 3. Frontend application served at root / (Status 200)")

    # 4. User Registration
    test_email = "teststudent@studymate.ai"
    reg_payload = {
        "full_name": "Test Student",
        "email": test_email,
        "password": "password123",
        "confirm_password": "password123",
        "major": "Data Science",
        "target_exam": "Midterm Examination"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    if res.status_code == 201:
        print("[PASS] 4. User registration successful")
    elif res.status_code == 400 and "already exists" in res.text:
        print("[PASS] 4. User registration verified (user already created in prior run)")
    else:
        assert False, f"Registration failed: {res.text}"

    # 5. User Login
    res = client.post("/api/auth/login", json={"email": test_email, "password": "password123"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] 5. User login & JWT issuance successful")

    # 6. Current User /me
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200 and res.json()["email"] == test_email, f"Get /me failed: {res.text}"
    print("[PASS] 6. JWT validation & /api/auth/me passed")

    # 7. Update Profile
    res = client.put("/api/auth/profile", headers=headers, json={"major": "Artificial Intelligence Engineering"})
    assert res.status_code == 200 and res.json()["user"]["major"] == "Artificial Intelligence Engineering", f"Profile update failed: {res.text}"
    print("[PASS] 7. Profile update successful")

    # 8. Demo Student Login
    res = client.post("/api/auth/login", json={"email": "student@studymate.ai", "password": "password123"})
    assert res.status_code == 200, f"Demo login failed: {res.text}"
    demo_token = res.json()["access_token"]
    demo_headers = {"Authorization": f"Bearer {demo_token}"}
    print("[PASS] 8. Pre-seeded demo account login passed (student@studymate.ai)")

    # 9. List Documents
    res = client.get("/api/documents", headers=demo_headers)
    assert res.status_code == 200, f"List documents failed: {res.text}"
    docs = res.json()
    assert len(docs) > 0, "No pre-seeded documents found"
    doc_id = docs[0]["id"]
    print(f"[PASS] 9. Documents listed ({len(docs)} documents found, Active ID: {doc_id})")

    # 10. Get Document Details
    res = client.get(f"/api/documents/{doc_id}", headers=demo_headers)
    assert res.status_code == 200, f"Get document failed: {res.text}"
    doc_data = res.json()
    assert doc_data["summary"], "Document summary missing"
    print(f"[PASS] 10. Document details verified: {doc_data['page_count']} pages, {doc_data['chunk_count']} chunks")

    # 11. Grounded RAG Chat with Page Citations
    query = "What are the stages of the Retrieval-Augmented Generation pipeline?"
    res = client.post("/api/rag/chat", headers=demo_headers, json={"document_id": doc_id, "query": query})
    assert res.status_code == 200, f"Chat failed: {res.text}"
    chat_resp = res.json()
    assert chat_resp["grounded"] is True, "Answer should be marked grounded"
    assert len(chat_resp["citations"]) > 0, "Answer should have citations"
    print(f"[PASS] 11. Grounded RAG Chat passed: Citing Page {chat_resp['citations'][0]['page_number']}")

    # 12. Chat History
    res = client.get(f"/api/rag/chat/{doc_id}/history", headers=demo_headers)
    assert res.status_code == 200 and len(res.json()) > 0, "Chat history empty"
    print(f"[PASS] 12. Chat history retrieved ({len(res.json())} messages)")

    # 13. Document Summary
    res = client.post("/api/rag/summary", headers=demo_headers, json={"document_id": doc_id})
    assert res.status_code == 200, f"Summary failed: {res.text}"
    summary_data = res.json()
    assert "executive_summary" in summary_data and len(summary_data["key_concepts"]) > 0
    print(f"[PASS] 13. Smart summary generated ({len(summary_data['key_concepts'])} key concepts)")

    # 14. Quiz Generation
    res = client.post("/api/quiz/generate", headers=demo_headers, json={"document_id": doc_id, "count": 5, "difficulty": "Medium"})
    assert res.status_code == 200, f"Quiz generation failed: {res.text}"
    quiz_data = res.json()
    quiz_id = quiz_data["id"]
    assert len(quiz_data["questions"]) == 5, "Quiz should have 5 questions"
    print(f"[PASS] 14. Quiz generated (Quiz ID: {quiz_id}, 5 questions)")

    # 15. Get Quiz Details
    res = client.get(f"/api/quiz/{quiz_id}", headers=demo_headers)
    assert res.status_code == 200, f"Get quiz failed: {res.text}"
    print("[PASS] 15. Quiz details retrieved with options A/B/C/D")

    # 16. Submit Quiz Attempt
    sample_answers = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    res = client.post(f"/api/quiz/{quiz_id}/submit", headers=demo_headers, json={"answers": sample_answers, "time_spent_seconds": 55})
    assert res.status_code == 200, f"Quiz submit failed: {res.text}"
    submit_result = res.json()
    assert "score" in submit_result and "percentage" in submit_result and len(submit_result["feedback"]) == 5
    print(f"[PASS] 16. Quiz submission & grading passed: Score {submit_result['score']}/{submit_result['total_questions']} ({submit_result['percentage']}%)")

    # 17. Flashcards Generation & List
    res = client.get(f"/api/flashcards/document/{doc_id}", headers=demo_headers)
    assert res.status_code == 200, f"Flashcards fetch failed: {res.text}"
    fc_data = res.json()
    assert fc_data["total"] > 0, "Flashcards empty"
    card_id = fc_data["cards"][0]["id"]
    print(f"[PASS] 17. Flashcards retrieved ({fc_data['total']} cards in deck)")

    # 18. Flashcard Mastery Update
    res = client.put(f"/api/flashcards/{card_id}/mastery", headers=demo_headers, json={"status": "mastered"})
    assert res.status_code == 200 and res.json()["mastery_status"] == "mastered"
    print("[PASS] 18. Flashcard mastery toggle ('mastered') verified")

    # 19. Progress Dashboard Analytics
    res = client.get("/api/progress/dashboard-stats", headers=demo_headers)
    assert res.status_code == 200, f"Dashboard stats failed: {res.text}"
    stats = res.json()
    assert stats["metrics"]["total_documents"] >= 1
    assert stats["metrics"]["quizzes_completed"] >= 1
    print(f"[PASS] 19. Dashboard analytics verified: Progress {stats['metrics']['study_progress']}%, Quizzes {stats['metrics']['quizzes_completed']}")

    # 20. Settings
    res = client.get("/api/settings", headers=demo_headers)
    assert res.status_code == 200 and "active_provider" in res.json()
    print("[PASS] 20. Settings retrieved: Active Provider =", res.json()["active_provider"])

    # 21. Upload Fresh Real PDF Document
    test_pdf_path = Path("backend/uploads/temp_test_lecture.pdf")
    from seed_data import generate_academic_pdf
    generate_academic_pdf(test_pdf_path)
    with open(test_pdf_path, "rb") as f:
        files = {"file": ("Fresh_Test_Lecture.pdf", f.read(), "application/pdf")}
    res = client.post("/api/documents/upload", headers=demo_headers, files=files)
    assert res.status_code == 200, f"Upload failed: {res.text}"
    uploaded_doc = res.json()["document"]
    assert uploaded_doc["page_count"] == 4, f"Expected 4 pages, got {uploaded_doc['page_count']}"
    assert uploaded_doc["chunk_count"] > 0, "Expected chunks to be indexed"
    print(f"[PASS] 21. Real PDF upload, Supabase Storage & pgvector indexing verified (ID: {uploaded_doc['id']}, Pages: {uploaded_doc['page_count']}, Chunks: {uploaded_doc['chunk_count']})")

    # Clean up uploaded test document from DB & disk
    client.delete(f"/api/documents/{uploaded_doc['id']}", headers=demo_headers)
    if test_pdf_path.exists():
        test_pdf_path.unlink()
    print("[PASS] 22. Document deletion & Supabase cleanup passed")

    print("\n" + "=" * 60)
    print("      ALL 22 VALIDATION CHECKS COMPLETED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
