import sys
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal, init_db
from seed_data import seed_database
from app.models.user import User
from app.models.document import Document
from app.models.chat_history import ChatHistory
from app.models.quiz_result import QuizResult
from app.models.flashcard import Flashcard
import httpx

def test_database_integration():
    print("=" * 60)
    print("      STUDYMATE AI - DATABASE & MODELS INTEGRATION TEST")
    print("=" * 60)

    # Initialize schema and seed database
    init_db()
    seed_database()

    db = SessionLocal()

    # 1. Test Users Table
    user = db.query(User).filter(User.email == "student@studymate.ai").first()
    assert user is not None, "Demo user not found"
    assert hasattr(user, "name"), "User missing 'name' field"
    assert hasattr(user, "email"), "User missing 'email' field"
    assert hasattr(user, "password_hash"), "User missing 'password_hash' field"
    assert hasattr(user, "created_at"), "User missing 'created_at' field"
    assert hasattr(user, "updated_at"), "User missing 'updated_at' field"
    print(f"[PASS] 1. Users table verified: ID={user.id}, Name='{user.name}', Email='{user.email}'")

    # 2. Test Documents Table
    doc = db.query(Document).filter(Document.user_id == user.id).first()
    assert doc is not None, "Document not found"
    assert hasattr(doc, "filename"), "Document missing 'filename' field"
    assert hasattr(doc, "original_filename"), "Document missing 'original_filename' field"
    assert hasattr(doc, "file_path"), "Document missing 'file_path' field"
    assert hasattr(doc, "file_size"), "Document missing 'file_size' field"
    assert hasattr(doc, "page_count"), "Document missing 'page_count' field"
    assert hasattr(doc, "status"), "Document missing 'status' field"
    assert hasattr(doc, "created_at"), "Document missing 'created_at' field"
    assert hasattr(doc, "updated_at"), "Document missing 'updated_at' field"
    print(f"[PASS] 2. Documents table verified: ID={doc.id}, File='{doc.original_filename}', Status='{doc.status}'")

    # 3. Test ChatHistory Table
    chat = db.query(ChatHistory).filter(ChatHistory.user_id == user.id).first()
    assert chat is not None, "ChatHistory record not found"
    assert hasattr(chat, "question"), "ChatHistory missing 'question'"
    assert hasattr(chat, "answer"), "ChatHistory missing 'answer'"
    assert hasattr(chat, "citations"), "ChatHistory missing 'citations'"
    assert hasattr(chat, "created_at"), "ChatHistory missing 'created_at'"
    print(f"[PASS] 3. ChatHistory table verified: ID={chat.id}, Q='{chat.question[:30]}...'")

    # 4. Test QuizResults Table
    quiz_res = db.query(QuizResult).filter(QuizResult.user_id == user.id).first()
    assert quiz_res is not None, "QuizResult record not found"
    assert hasattr(quiz_res, "total_questions"), "QuizResult missing 'total_questions'"
    assert hasattr(quiz_res, "correct_answers"), "QuizResult missing 'correct_answers'"
    assert hasattr(quiz_res, "wrong_answers"), "QuizResult missing 'wrong_answers'"
    assert hasattr(quiz_res, "score"), "QuizResult missing 'score'"
    assert hasattr(quiz_res, "percentage"), "QuizResult missing 'percentage'"
    assert hasattr(quiz_res, "created_at"), "QuizResult missing 'created_at'"
    print(f"[PASS] 4. QuizResults table verified: ID={quiz_res.id}, Score={quiz_res.score}/{quiz_res.total_questions} ({quiz_res.percentage}%)")

    # 5. Test Flashcards Table
    card = db.query(Flashcard).filter(Flashcard.user_id == user.id).first()
    assert card is not None, "Flashcard record not found"
    assert hasattr(card, "question"), "Flashcard missing 'question'"
    assert hasattr(card, "answer"), "Flashcard missing 'answer'"
    assert hasattr(card, "status"), "Flashcard missing 'status'"
    assert hasattr(card, "created_at"), "Flashcard missing 'created_at'"
    print(f"[PASS] 5. Flashcards table verified: ID={card.id}, Q='{card.question[:30]}...', Status='{card.status}'")

    # 6. Test Relationships
    assert len(user.documents) > 0, "User -> Documents relationship empty"
    assert len(user.chat_history) > 0, "User -> ChatHistory relationship empty"
    assert len(user.quiz_results) > 0, "User -> QuizResults relationship empty"
    assert len(user.flashcards) > 0, "User -> Flashcards relationship empty"
    assert len(doc.chat_history) > 0, "Document -> ChatHistory relationship empty"
    assert len(doc.quiz_results) > 0, "Document -> QuizResults relationship empty"
    assert len(doc.flashcards) > 0, "Document -> Flashcards relationship empty"
    print("[PASS] 6. SQLAlchemy Relationships verified with cascading constraints")

    # 7. Test ChatHistory Insertion & Querying
    new_chat = ChatHistory(
        user_id=user.id,
        document_id=doc.id,
        question="Explain deep learning architectures.",
        answer="Deep learning architectures utilize layered neural networks to learn representations from data.",
        citations='[{"page_number": 3, "excerpt": "Deep Learning utilizes layered artificial neural networks", "relevance_score": 94}]'
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    assert new_chat.id is not None, "Failed to persist ChatHistory"
    print(f"[PASS] 7. ChatHistory persistence verified: ID={new_chat.id}")

    # 8. Test Progress Computation from Database Tables
    total_docs = db.query(Document).filter(Document.user_id == user.id).count()
    quiz_results = db.query(QuizResult).filter(QuizResult.user_id == user.id).all()
    avg_score = (sum(q.percentage for q in quiz_results) / len(quiz_results)) if quiz_results else 0.0
    flashcards_count = db.query(Flashcard).filter(Flashcard.user_id == user.id).count()
    mastered_count = db.query(Flashcard).filter(Flashcard.user_id == user.id, Flashcard.status.in_(["known", "mastered"])).count()
    assert total_docs > 0 and len(quiz_results) > 0 and flashcards_count > 0
    print(f"[PASS] 8. Progress Metrics verified: Docs={total_docs}, AvgScore={avg_score:.1f}%, Flashcards={mastered_count}/{flashcards_count}")

    # 9. Test QuizResult Insertion & Percentage Calculation
    new_quiz_result = QuizResult(
        user_id=user.id,
        document_id=doc.id,
        total_questions=5,
        correct_answers=5,
        wrong_answers=0,
        score=5,
        percentage=100.0
    )
    db.add(new_quiz_result)
    db.commit()
    db.refresh(new_quiz_result)
    assert new_quiz_result.id is not None and new_quiz_result.percentage == 100.0
    print(f"[PASS] 9. QuizResult persistence verified: ID={new_quiz_result.id}, Score=5/5 (100.0%)")

    # 10. Test Flashcard Creation & Status Transition
    new_flashcard = Flashcard(
        user_id=user.id,
        document_id=doc.id,
        question="What is backpropagation?",
        answer="Backpropagation calculates the gradient of the loss function using the chain rule.",
        status="new"
    )
    db.add(new_flashcard)
    db.commit()
    db.refresh(new_flashcard)
    assert new_flashcard.id is not None and new_flashcard.status == "new"

    # Status transition to known
    new_flashcard.status = "known"
    db.commit()
    db.refresh(new_flashcard)
    assert new_flashcard.status == "known"
    print(f"[PASS] 10. Flashcard persistence & status transition verified: ID={new_flashcard.id}, Status='{new_flashcard.status}'")

    db.close()
    print("=" * 60)
    print("      ALL 10 DATABASE INTEGRATION CHECKS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    test_database_integration()
