import os
import sys
import json
import shutil
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import settings
from database import (
    init_db,
    SessionLocal,
    User,
    Document,
    DocumentChunk,
    Quiz,
    QuizAttempt,
    QuizResult,
    Flashcard,
    ChatMessage,
    ChatHistory,
    ActivityLog
)
from auth import hash_password
from pdf_processor import extract_text_from_pdf, chunk_document
from app.services.gemini_service import gemini_service
from app.services.supabase_service import supabase_service


def generate_academic_pdf(file_path: Path):
    """Generates a valid 4-page academic PDF with comprehensive computer science study content."""
    pages_content = [
        # Page 1
        [
            "Foundations of Artificial Intelligence (Page 1)",
            "Artificial Intelligence is defined as the capability of computational systems to perform tasks that typically require human intelligence.",
            "Historical foundations date back to Alan Turing's 1950 seminal paper proposing the Turing Test as an empirical measure of machine intelligence.",
            "Modern AI distinguishes between Narrow AI, designed for specific discrete tasks like image classification, and General AI (AGI), which possesses generalized reasoning.",
            "Core components of modern AI include knowledge representation, heuristic search, automated planning, and probabilistic reasoning.",
            "Knowledge graphs and symbolic rule engines formed early symbolic AI, while connectionist models and statistical learning dominate modern architectures.",
            "Ethical considerations in AI involve algorithmic bias, data privacy, accountability, and the transparency of autonomous decision systems."
        ],
        # Page 2
        [
            "Machine Learning Paradigms and Principles (Page 2)",
            "Machine Learning is a subset of artificial intelligence enabling computational models to learn patterns from training data without explicit deterministic rules.",
            "Supervised Learning trains models on labeled datasets consisting of input-output pairs to solve classification and continuous regression problems.",
            "Common supervised algorithms include Linear Regression, Logistic Regression, Support Vector Machines (SVM), and Random Forest ensembles.",
            "Unsupervised Learning discovers latent structures and clusters in unlabeled data without predefined ground truth targets.",
            "Key unsupervised techniques include K-Means Clustering, Principal Component Analysis (PCA), and Hierarchical Density-Based Spatial Clustering.",
            "Reinforcement Learning operates through an autonomous agent interacting with an environment to maximize cumulative scalar rewards via trial and error."
        ],
        # Page 3
        [
            "Deep Neural Networks and Transformer Architectures (Page 3)",
            "Deep Learning utilizes layered artificial neural networks to learn hierarchical abstractions and distributed representations from raw unstructured data.",
            "A standard Multi-Layer Perceptron (MLP) passes inputs through hidden activation layers using non-linear functions such as ReLU, Sigmoid, or GELU.",
            "Backpropagation combined with Stochastic Gradient Descent (SGD) optimizes weight matrices by calculating the gradient of the loss function via chain rule.",
            "Convolutional Neural Networks (CNN) excel at spatial feature extraction in computer vision through localized receptive fields and pooling.",
            "The Transformer architecture introduced by Vaswani et al. replaced recurrent networks with multi-head self-attention mechanisms.",
            "Self-attention computes dynamic weightings between all tokens in a sequence simultaneously, allowing scalable parallel training on massive corpora."
        ],
        # Page 4
        [
            "Retrieval-Augmented Generation (RAG) and Citation Mechanics (Page 4)",
            "Retrieval-Augmented Generation is an architectural framework that anchors Large Language Models by retrieving relevant external document passages.",
            "Standard LLMs often suffer from hallucination and temporal knowledge obsolescence because their parametric weights cannot verify private or recent facts.",
            "The RAG pipeline operates in three distinct stages: document chunking, dense vector embedding generation, and cosine similarity vector retrieval.",
            "In modern RAG systems, vector databases such as ChromaDB store high-dimensional embeddings paired with page-level metadata and provenance.",
            "When a student submits a question, the vector index performs nearest-neighbor search to retrieve the top-k most semantically relevant chunks.",
            "Strict grounding prompts mandate that the language model synthesize answers exclusively from retrieved excerpts and display verified page-wise citations."
        ]
    ]

    objects = [None, None] # 1: Catalog, 2: Pages
    page_ids = []
    content_ids = []

    for page_lines in pages_content:
        # Build text stream with positioning
        stream_parts = ["BT", "/F1 11 Tf", "16 TL"]
        # Start at top left (x=50, y=720)
        stream_parts.append("50 720 Td")
        for idx, line in enumerate(page_lines):
            # Escape parentheses in PDF text
            safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if idx == 0:
                # Title line
                stream_parts.append(f"({safe_line}) Tj")
                stream_parts.append("T*")
                stream_parts.append("T*") # extra line feed
            else:
                stream_parts.append(f"({safe_line}) Tj")
                stream_parts.append("T*")
        stream_parts.append("ET")
        stream_text = "\n".join(stream_parts)

        c_id = len(objects) + 1
        objects.append(f"<< /Length {len(stream_text)} >>\nstream\n{stream_text}\nendstream")
        p_id = len(objects) + 1
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {c_id} 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>")
        content_ids.append(c_id)
        page_ids.append(p_id)

    kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[0] = "<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>"

    with open(file_path, "wb") as f:
        f.write(b"%PDF-1.4\n")
        offsets = [0]
        for i, obj in enumerate(objects):
            offset = f.tell()
            offsets.append(offset)
            f.write(f"{i+1} 0 obj\n{obj}\nendobj\n".encode("latin-1"))

        start_xref = f.tell()
        f.write(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("latin-1"))
        for off in offsets[1:]:
            f.write(f"{off:010d} 00000 n \n".encode("latin-1"))
        f.write(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start_xref}\n%%EOF\n".encode("latin-1"))


def seed_database():
    init_db()
    db = SessionLocal()

    # 1. Create Demo User
    demo_email = "student@studymate.ai"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        user = User(
            email=demo_email,
            full_name="Alex Chen",
            hashed_password=hash_password("password123"),
            major="Computer Science & Artificial Intelligence",
            target_exam="Semester Finals & AI Certification"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created demo user: {demo_email} / password123")

    # 2. Check or Create Sample Document
    doc = db.query(Document).filter(Document.user_id == user.id).first()
    if not doc:
        sample_pdf_name = "Introduction_to_Artificial_Intelligence_and_RAG.pdf"
        sample_pdf_path = settings.UPLOAD_DIR / sample_pdf_name
        generate_academic_pdf(sample_pdf_path)
        file_size = sample_pdf_path.stat().st_size

        doc = Document(
            user_id=user.id,
            filename=sample_pdf_name,
            original_name="Introduction to Artificial Intelligence and RAG.pdf",
            file_size=file_size,
            status="processing"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Extract, chunk, embed
        extracted = extract_text_from_pdf(sample_pdf_path)
        chunks = chunk_document(extracted["pages"], chunk_size=550, chunk_overlap=90)

        chunk_records = []
        for c in chunks:
            emb = gemini_service.generate_embedding(c["content"])
            chunk_records.append(DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                content=c["content"],
                embedding_json=json.dumps(emb)
            ))
        db.bulk_save_objects(chunk_records)
        db.commit()

        # Summary via Central Gemini Service
        summary_data = gemini_service.generate_summary(extracted["full_text"], extracted["pages"])
        doc.summary = summary_data["executive_summary"]
        doc.key_points_json = json.dumps(summary_data["key_concepts"])
        doc.page_count = extracted["total_pages"]
        doc.chunk_count = len(chunks)
        doc.storage_path = f"documents/{sample_pdf_name}"
        doc.status = "ready"
        db.commit()

        # Clean up temporary PDF file immediately so no disk files linger
        try:
            if sample_pdf_path.exists():
                sample_pdf_path.unlink()
        except Exception:
            pass

        # Seed initial Quizzes via Central Gemini Service
        quiz_questions = gemini_service.generate_quiz(chunks, count=5, difficulty="Medium")
        quiz = Quiz(
            document_id=doc.id,
            user_id=user.id,
            title="AI Foundations & RAG Mastery Quiz",
            topic="Artificial Intelligence & RAG",
            difficulty="Medium",
            total_questions=len(quiz_questions),
            questions_json=json.dumps(quiz_questions)
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        # Seed initial Quiz Attempt & Quiz Result
        attempt = QuizAttempt(
            quiz_id=quiz.id,
            document_id=doc.id,
            user_id=user.id,
            score=4,
            total_questions=5,
            percentage=80.0,
            answers_json=json.dumps({"1": 0, "2": 0, "3": 0, "4": 0, "5": 1}),
            time_spent_seconds=85
        )
        db.add(attempt)

        quiz_res = QuizResult(
            user_id=user.id,
            document_id=doc.id,
            total_questions=5,
            correct_answers=4,
            wrong_answers=1,
            score=4,
            percentage=80.0
        )
        db.add(quiz_res)

        # Seed Flashcards via Central Gemini Service
        flashcards = gemini_service.generate_flashcards(chunks, count=6)
        for i, fc in enumerate(flashcards):
            card = Flashcard(
                document_id=doc.id,
                user_id=user.id,
                front=fc["front"],
                back=fc["back"],
                topic=fc["topic"],
                page_number=fc["page_number"],
                mastery_status="mastered" if i < 3 else "learning",
                times_reviewed=2 if i < 3 else 0
            )
            db.add(card)

        # Seed initial Chat Messages with Citation
        msg1 = ChatMessage(
            document_id=doc.id,
            user_id=user.id,
            role="user",
            content="What are the main stages of the RAG pipeline?"
        )
        db.add(msg1)
        db.commit()

        msg2 = ChatMessage(
            document_id=doc.id,
            user_id=user.id,
            role="assistant",
            content="According to **Page 4** of your uploaded study material, the Retrieval-Augmented Generation (RAG) pipeline operates across three foundational stages:\n\n1. **Document Chunking**: Extracting text page-by-page and splitting it into semantically coherent overlapping segments.\n2. **Dense Vector Embeddings**: Transforming text chunks into high-dimensional numerical vectors.\n3. **Cosine Similarity Retrieval**: Querying the vector database (ChromaDB) to retrieve top-k semantically relevant chunks with verified page provenance.",
            citations_json=json.dumps([
                {
                    "page_number": 4,
                    "excerpt": "The RAG pipeline operates in three distinct stages: document chunking, dense vector embedding generation, and cosine similarity vector retrieval.",
                    "relevance_score": 96
                }
            ])
        )
        db.add(msg2)

        chat_hist = ChatHistory(
            user_id=user.id,
            document_id=doc.id,
            question="What are the main stages of the RAG pipeline?",
            answer="According to Page 4 of your uploaded study material, the Retrieval-Augmented Generation (RAG) pipeline operates across three foundational stages: 1) Document Chunking, 2) Dense Vector Embeddings, 3) Cosine Similarity Retrieval.",
            citations=json.dumps([
                {
                    "page_number": 4,
                    "excerpt": "The RAG pipeline operates in three distinct stages: document chunking, dense vector embedding generation, and cosine similarity vector retrieval.",
                    "relevance_score": 96
                }
            ])
        )
        db.add(chat_hist)

        # Activities
        db.add(ActivityLog(
            user_id=user.id,
            activity_type="upload",
            title="Uploaded 'Introduction to Artificial Intelligence and RAG.pdf'",
            description="Extracted 4 pages, 8 chunks and created ChromaDB embeddings."
        ))
        db.add(ActivityLog(
            user_id=user.id,
            activity_type="quiz",
            title="Completed Quiz: 80%",
            description="Scored 4/5 in 'AI Foundations & RAG Mastery Quiz'."
        ))
        db.add(ActivityLog(
            user_id=user.id,
            activity_type="chat",
            title="Asked: 'What are the main stages of the RAG pipeline?'",
            description="Received grounded answer with citations to Page 4."
        ))
        db.commit()
        print("Database seeded with sample document, quiz, flashcards, and citations!")

    db.close()


if __name__ == "__main__":
    seed_database()
