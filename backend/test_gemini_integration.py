import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.services.gemini_service import gemini_service

client = TestClient(app)

def test_all_gemini_features():
    print("\n" + "=" * 70)
    print("  STUDYMATE AI — GOOGLE GEMINI AI INTEGRATION TEST SUITE")
    print("=" * 70)

    # 1. Test Health & Gemini Status
    print("\n[TEST 1] Verifying System Health & Gemini Configuration...")
    health_res = client.get("/api/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    health_data = health_res.json()
    print("  [OK] Health Status:", health_data.get("status"))
    print("  [OK] Database Engine:", health_data.get("database"))
    print("  [OK] AI Engine:", health_data.get("ai_engine"))
    print("  [OK] Gemini SDK is_configured:", gemini_service.is_configured())

    # 2. Test 1: AI Chatbot (/api/gemini/chat)
    print("\n[TEST 2] Testing Endpoint 1: AI Chatbot (/api/gemini/chat)...")
    chat_payload = {
        "message": "Explain the concept of asymptotic runtime complexity in computer science.",
        "history": [
            {"role": "user", "content": "What is Big O notation?"},
            {"role": "assistant", "content": "Big O notation describes the upper bound of an algorithm's growth rate."}
        ],
        "system_instruction": "You are StudyMate AI, an academic study assistant."
    }
    chat_res = client.post("/api/gemini/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    assert "reply" in chat_data, "Chat response missing 'reply'"
    assert len(chat_data["reply"]) > 20, "Reply content too short"
    print("  [OK] Chat Reply Status: 200 OK")
    print("  [OK] Model Reported:", chat_data.get("model"))
    print("  [OK] Reply Excerpt:", chat_data["reply"][:90].replace("\n", " "), "...")

    # 3. Test 2: Ask Study Questions (/api/gemini/ask)
    print("\n[TEST 3] Testing Endpoint 2: Ask Study Questions (/api/gemini/ask)...")
    ask_payload = {
        "question": "What is the primary difference between a process and a thread?",
        "context": "A process has its own address space, whereas threads share the memory space of their parent process."
    }
    ask_res = client.post("/api/gemini/ask", json=ask_payload)
    assert ask_res.status_code == 200, f"Ask question failed: {ask_res.text}"
    ask_data = ask_res.json()
    assert "answer" in ask_data, "Ask response missing 'answer'"
    assert "key_takeaways" in ask_data, "Ask response missing 'key_takeaways'"
    assert isinstance(ask_data["key_takeaways"], list), "key_takeaways should be a list"
    print("  [OK] Ask Question Status: 200 OK")
    print("  [OK] Confidence Score:", ask_data.get("confidence"), "%")
    print("  [OK] Key Takeaways Count:", len(ask_data["key_takeaways"]))
    print("  [OK] Answer Excerpt:", ask_data["answer"][:90].replace("\n", " "), "...")

    # 4. Test 3: Notes Generation (/api/gemini/notes)
    print("\n[TEST 4] Testing Endpoint 3: Notes Generation (/api/gemini/notes)...")
    notes_payload = {
        "topic": "Relational Database Normalization (1NF, 2NF, 3NF, BCNF)",
        "style": "comprehensive"
    }
    notes_res = client.post("/api/gemini/notes", json=notes_payload)
    assert notes_res.status_code == 200, f"Notes generation failed: {notes_res.text}"
    notes_data = notes_res.json()
    assert "title" in notes_data, "Notes missing 'title'"
    assert "notes_markdown" in notes_data, "Notes missing 'notes_markdown'"
    assert "key_definitions" in notes_data, "Notes missing 'key_definitions'"
    print("  [OK] Notes Generation Status: 200 OK")
    print("  [OK] Generated Title:", notes_data.get("title"))
    print("  [OK] Style:", notes_data.get("style"))
    print("  [OK] Word Count:", notes_data.get("word_count"))
    print("  [OK] Key Definitions Extracted:", len(notes_data["key_definitions"]))

    # 5. Test 4: Notes & Document Summarization (/api/gemini/summarize)
    print("\n[TEST 5] Testing Endpoint 4: Notes Summarization (/api/gemini/summarize)...")
    sample_text = (
        "Operating systems coordinate computational resources including the CPU, main memory, "
        "and peripheral devices. The kernel manages process scheduling using algorithms such as "
        "Round Robin, Shortest Job First, and Multi-level Feedback Queues. Virtual memory enables "
        "isolated process execution through paging and translation lookaside buffers."
    )
    sum_payload = {
        "content": sample_text,
        "summary_type": "executive"
    }
    sum_res = client.post("/api/gemini/summarize", json=sum_payload)
    assert sum_res.status_code == 200, f"Summarize failed: {sum_res.text}"
    sum_data = sum_res.json()
    assert "summary" in sum_data, "Summary response missing 'summary'"
    assert "key_concepts" in sum_data, "Summary missing 'key_concepts'"
    print("  [OK] Summarization Status: 200 OK")
    print("  [OK] Executive Summary:", sum_data["summary"][:90], "...")
    print("  [OK] Key Concepts Identified:", sum_data["key_concepts"])
    print("  [OK] Reading Time:", sum_data.get("reading_time_minutes"), "min")

    # 6. Test 5: MCQ Generation (/api/gemini/mcq)
    print("\n[TEST 6] Testing Endpoint 5: MCQ Generation (/api/gemini/mcq)...")
    mcq_payload = {
        "topic": "Binary Search Trees and AVL Trees",
        "count": 3,
        "difficulty": "Medium"
    }
    mcq_res = client.post("/api/gemini/mcq", json=mcq_payload)
    assert mcq_res.status_code == 200, f"MCQ generation failed: {mcq_res.text}"
    mcq_data = mcq_res.json()
    assert "questions" in mcq_data, "MCQ missing 'questions'"
    questions = mcq_data["questions"]
    assert len(questions) == 3, f"Expected 3 questions, got {len(questions)}"
    for q in questions:
        assert "question" in q
        assert "options" in q
        assert len(q["options"]) == 4, "MCQ must have exactly 4 choices"
        assert "correct_answer_index" in q
        assert 0 <= q["correct_answer_index"] < 4
        assert "explanation" in q
    print("  [OK] MCQ Generation Status: 200 OK")
    print("  [OK] Generated", len(questions), "MCQs successfully")
    print("  [OK] Sample Question 1:", questions[0]["question"])
    print("  [OK] Choices Count:", len(questions[0]["options"]))
    print("  [OK] Correct Answer Index:", questions[0]["correct_answer_index"])

    # 7. Test 6: Quiz Generation (/api/gemini/quiz)
    print("\n[TEST 7] Testing Endpoint 6: Quiz Generation (/api/gemini/quiz)...")
    quiz_payload = {
        "topic": "Computer Networks: TCP/IP Stack & OSI Model",
        "count": 4,
        "difficulty": "Medium",
        "title": "Computer Networks Midterm Practice Exam"
    }
    quiz_res = client.post("/api/gemini/quiz", json=quiz_payload)
    assert quiz_res.status_code == 200, f"Quiz generation failed: {quiz_res.text}"
    quiz_data = quiz_res.json()
    assert "questions" in quiz_data, "Quiz missing 'questions'"
    assert "title" in quiz_data
    assert "total_questions" in quiz_data
    assert quiz_data["total_questions"] == 4
    print("  [OK] Quiz Generation Status: 200 OK")
    print("  [OK] Quiz Title:", quiz_data["title"])
    print("  [OK] Difficulty:", quiz_data["difficulty"])
    print("  [OK] Total Questions:", quiz_data["total_questions"])
    print("  [OK] Estimated Time:", quiz_data.get("estimated_time_minutes"), "minutes")

    # 8. Test 7: API Input Validation & Error Handling
    print("\n[TEST 8] Testing API Validation & Error Handling...")
    invalid_notes = client.post("/api/gemini/notes", json={})
    assert invalid_notes.status_code == 400, "Should reject empty notes request with 400"
    print("  [OK] Empty notes payload correctly rejected (HTTP 400):", invalid_notes.json().get("detail"))

    invalid_sum = client.post("/api/gemini/summarize", json={})
    assert invalid_sum.status_code == 400, "Should reject empty summarize request with 400"
    print("  [OK] Empty summarize payload correctly rejected (HTTP 400):", invalid_sum.json().get("detail"))

    print("\n" + "=" * 70)
    print("  ALL 8/8 GEMINI INTEGRATION & ENDPOINT TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    test_all_gemini_features()
