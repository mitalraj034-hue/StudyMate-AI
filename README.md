# 🤖 StudyMate AI — AI-Powered Grounded Academic Study Platform

> **Study Smarter. Learn Faster. With StudyMate AI.**  
> A production-grade educational platform powered by **Retrieval-Augmented Generation (RAG)** that turns your course notes and textbooks into grounded study assistants with zero hallucinations, verified page citations, interactive MCQ quizzes, and active recall flashcards.

---

## 🌟 Key Capabilities & Features

### 1. 📄 Page-by-Page PDF Processing & ChromaDB Vector Indexing
- **Drag-and-drop & Browse**: Upload lecture slides, textbook chapters, or academic papers (up to 25MB).
- **Page-wise Extraction**: Preserves exact page numbers for every extracted passage using `pypdf`.
- **Intelligent Chunking**: Sliding-window semantic chunker maintaining strict page provenance.
- **Persistent Vector Database**: Chunks are embedded and indexed in **ChromaDB** with dense contextual representations.

### 2. 💬 Zero-Hallucination AI Document Chat with Page Citations
- **Strict Grounding Guardrails**: Answers are synthesized **strictly** from retrieved document chunks.
- **Clickable Page Citations**: Every response includes clickable citation chips (e.g. `[Page 4 (96% match)]`).
- **Source Excerpt Modal**: Clicking a citation opens a modal displaying the exact raw excerpt from that page and a quick copy button.
- **Suggested Study Prompts**: Instant one-click inquiry chips for quick revision.

### 3. 📝 Smart Document Summaries
- **Executive Overview**: High-level synthesis of complex multi-page readings.
- **Key Concepts Tag Cloud**: Auto-extracted technical terms and definitions.
- **Section & Page Breakdown**: Chronological highlights by page number.
- **Reading Time Estimate**: Calculated based on average academic reading speed.

### 4. 🧠 Adaptive MCQ Quiz Generator & Exam Simulator
- **Auto-Generated Questions**: Formulates multiple-choice questions grounded in factual propositions from the document.
- **Configurable Difficulty & Length**: Select between Easy, Medium, Hard, and 3 to 8 questions.
- **Interactive Exam Player**: Sleek UI with options A/B/C/D, progress indicator, and answer selection.
- **Instant Grading & Explanations**: Immediate score percentage, correct answer highlighting, and page-wise academic citations for every answer.
- **Attempt History Tracking**: Saves scores, percentages, and timestamps in database.

### 5. 🃏 Active Recall 3D Flip Flashcards
- **Interactive 3D Flip Card Effect**: Click to smoothly flip between Question (Front) and Answer/Definition (Back).
- **Mastery State Tracking**: Mark cards as **"Still Learning"** (amber) or **"Mastered"** (emerald).
- **Deck Progress Bar**: Real-time mastery percentage calculation.
- **Deck Shuffling**: Randomizes study sequence to enhance memory retention.

### 6. 📊 Student Learning Analytics & Progress Dashboard
- **Key Metrics**:
  - Total Documents Indexed
  - Total Inquiries Asked
  - Quizzes Completed
  - Average Quiz Score (%)
  - Syllabus Study Progress (%)
- **Continue Studying Section**: Quick 1-click resumption of the most recent reading.
- **Recent Activity Stream**: Audit trail of uploads, quizzes, and chat inquiries.
- **Quiz Performance Table**: Complete historical score table with pass/review status.

### 7. 🔒 Secure Authentication & Student Profile
- Secure registration with Full Name, Email, Password, Major/Degree, and Target Exam.
- JWT-based authentication with bcrypt password hashing.
- Student profile editor to update target exams and passwords.
- Simulated password recovery UI.

### 8. ⚡ Flexible AI Engine (Claude 3, OpenAI GPT-4o, or Built-in Local RAG)
- **Built-in Grounded Engine**: Runs out of the box with **zero** external API key required! Perfect for offline use, grading, or local development.
- **Claude / OpenAI / Gemini Ready**: Plug in your `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in the **Settings** tab or `.env` to elevate to Anthropic Claude 3 or GPT-4o on the fly.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User["Student User"]
    PDF["Uploaded PDF Notes"]
    
    subgraph Frontend["React 18 + Tailwind CSS"]
        UI["Student Dashboard & Workspace"]
        Chat["Grounded AI Chat"]
        Quiz["MCQ Quiz Player"]
        FC["3D Flashcards"]
        Analytics["Progress Analytics"]
    end
    
    subgraph Backend["FastAPI REST Server"]
        Auth["JWT Auth & Security"]
        Extractor["PyPDF Page-by-Page Parser"]
        Chunker["Provenance Text Chunker"]
        RAG["RAG Engine & Grounding Guardrails"]
        DB[(SQLite / PostgreSQL)]
    end
    
    subgraph VectorMemory["Vector Storage & AI"]
        Chroma[("ChromaDB Vector Store")]
        Embeddings["StudyMate Dense Vector Embeddings"]
        LLM["Claude 3 / OpenAI GPT-4o / Local Extractor"]
    end
    
    User --> UI
    PDF --> UI
    UI -->|Upload Multipart| Extractor
    Extractor -->|Page-wise Text| Chunker
    Chunker -->|Dense Embeddings| Chroma
    Chunker -->|Save Chunks| DB
    
    Chat -->|Query| RAG
    RAG -->|Similarity Search| Chroma
    Chroma -->|Top-k Chunks + Page Provenance| RAG
    RAG -->|Grounding Prompt| LLM
    LLM -->|Answer + Citations| Chat
    
    RAG -->|Generate MCQs| Quiz
    RAG -->|Generate Cards| FC
    Quiz -->|Save Scores| DB
    DB --> Analytics
```

---

## 🐘 PostgreSQL Database & Alembic Migrations Guide

StudyMate AI uses **PostgreSQL** as its primary relational database for persistent application data, and **ChromaDB** separately for vector embeddings and RAG retrieval.

### Database Tables & Schema
- **`users`**: `id`, `name`, `email` (unique), `password_hash`, `created_at`, `updated_at`
- **`documents`**: `id`, `user_id` (FK to `users`), `filename`, `original_filename`, `file_path`, `file_size`, `page_count`, `status`, `created_at`, `updated_at`
- **`chat_history`**: `id`, `user_id` (FK to `users`), `document_id` (FK to `documents`), `question`, `answer`, `citations`, `created_at`
- **`quiz_results`**: `id`, `user_id` (FK to `users`), `document_id` (FK to `documents`), `total_questions`, `correct_answers`, `wrong_answers`, `score`, `percentage`, `created_at`
- **`flashcards`**: `id`, `user_id` (FK to `users`), `document_id` (FK to `documents`), `question`, `answer`, `status` (`new`, `known`, `review`), `created_at`

---

### Step-by-Step Setup Guide (Beginner Friendly)

#### Step 1: Install PostgreSQL
- **Windows**: Download and run the official installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/). During installation, set your password (e.g. `postgres`) and note down the port (`5432`).
- **macOS**: Install via Homebrew: `brew install postgresql@16 && brew services start postgresql@16`
- **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install postgresql postgresql-contrib`
- **Docker (Alternative)**:
  ```bash
  docker run --name studymate-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=studymate_ai -p 5432:5432 -d postgres:16
  ```

#### Step 2: Create the Database
Open **SQL Shell (psql)** or run from your terminal:
```sql
CREATE DATABASE studymate_ai;
```
*(Verify by typing `\l` in psql to see `studymate_ai` in the database list).*

#### Step 3: Install Dependencies
Install all required packages including SQLAlchemy, modern Psycopg 3, and Alembic:
```bash
pip install -r requirements.txt
```

#### Step 4: Configure `.env`
Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```
Open `backend/.env` (or root `.env`) and set your PostgreSQL credentials:
```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/studymate_ai
SECRET_KEY=studymate_ai_super_secret_jwt_key_2026_academic_rag
CLAUDE_API_KEY=your_optional_claude_key
```
> *Replace `YOUR_PASSWORD` with your actual PostgreSQL superuser password.*

#### Step 5: Run Alembic Migrations
Run the initial migration to create all tables and indexes:
```bash
cd backend
alembic upgrade head
```
You will see:
```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Running upgrade -> 0001_initial_schema, Initial migration: users, documents, chat_history, quiz_results, flashcards
```

#### Step 6: Start FastAPI
Launch the backend server:
```bash
# From repository root:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Or from backend/ directory:
uvicorn app.main:app --reload
```

#### Step 7: Verify Through Swagger UI (`/docs`)
1. Open your browser and navigate to: **`http://127.0.0.1:8000/docs`**
2. Expand **`POST /api/auth/register`** -> click **Try it out** -> enter registration details -> click **Execute**. You should receive HTTP `201 Created` with a JWT token.
3. Click the green **Authorize** button at the top right and enter your Bearer token.
4. Test **`POST /api/documents/upload`**, **`POST /api/chat`**, and **`POST /api/quiz/submit`** to verify data persisting directly into PostgreSQL tables!

---

| Layer | Technologies Used |
|---|---|
| **Frontend** | React 18, Tailwind CSS, Lucide React, Vite, Modern Responsive Design |
| **Backend** | Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, PyJWT, bcrypt |
| **Document Processing** | PyPDF (Page-by-page extraction, OCR normalization, token estimators) |
| **Vector Database** | ChromaDB (Persistent vector store with subword hash embeddings) |
| **Relational Database** | SQLite (Default for zero-config run) or PostgreSQL (Production ready) |
| **AI / RAG** | Retrieval-Augmented Generation with strict citations, Claude 3 / OpenAI / Gemini API support |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (Python 3.13 tested and verified)
- Node.js 18+ and npm

---

### Option 1: Quick Run (One-Click)

Simply double-click or run:
```cmd
run.bat
```
This automatically:
1. Seeds the database with a rich 4-page academic study guide on **"Artificial Intelligence and RAG"**.
2. Pre-configures a demo student account.
3. Launches the unified server on **`http://127.0.0.1:8000`** serving both the API and the React frontend!

---

### Option 2: Full Development Mode (Vite Hot-Reload + FastAPI)

Run:
```cmd
start_dev.bat
```
Or start each service in separate terminals:

#### Terminal 1 — Backend:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 — Frontend:
```bash
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 🔑 Pre-Seeded Student Credentials

For instant evaluation without creating an account:

| Field | Value |
|---|---|
| **Email** | `student@studymate.ai` |
| **Password** | `password123` |
| **Full Name** | Alex Chen |
| **Pre-loaded Doc** | Introduction to Artificial Intelligence and RAG (4 Pages, 8 Chunks) |

*(You can also click the **"Instant Demo Account"** button on the landing page or the **"Fill Pre-Seeded Student Credentials"** button on the login screen!)*

---

## 📡 REST API Reference (Postman Compatible)

All endpoints accept and return JSON. Authenticated endpoints require `Authorization: Bearer <access_token>`.

### Authentication
- `POST /api/auth/register` — Create a new student account
- `POST /api/auth/login` — Sign in and receive JWT token
- `GET /api/auth/me` — Retrieve authenticated user profile
- `PUT /api/auth/profile` — Update student name, major, target exam, or password
- `POST /api/auth/forgot-password` — Password recovery simulator

### Documents
- `POST /api/documents/upload` — Upload multipart PDF, extracts pages, chunks text, and indexes in ChromaDB
- `GET /api/documents` — List user's documents (supports `?query=` search filter)
- `GET /api/documents/{id}` — Get document metadata, executive summary, and key concepts
- `DELETE /api/documents/{id}` — Delete document, its file, and its ChromaDB vector index

### Grounded RAG & Chat
- `POST /api/rag/chat` — Submit inquiry; returns grounded answer with page citations
  ```json
  {
    "document_id": 1,
    "query": "What are the three stages of the RAG pipeline?"
  }
  ```
- `GET /api/rag/chat/{doc_id}/history` — Retrieve full conversation history for document
- `POST /api/rag/summary` — Generate structured executive summary & key concept breakdown

### MCQ Quizzes
- `POST /api/quiz/generate` — Generate MCQs (`count`, `difficulty`, `document_id`)
- `GET /api/quiz/{quiz_id}` — Get quiz questions
- `POST /api/quiz/{quiz_id}/submit` — Grade answers; returns percentage and page-wise explanations
- `GET /api/quiz/document/{doc_id}` — List past quizzes for document

### Active Recall Flashcards
- `POST /api/flashcards/generate` — Generate study cards (`document_id`, `count`)
- `GET /api/flashcards/document/{doc_id}` — Fetch flashcards with deck mastery statistics
- `PUT /api/flashcards/{card_id}/mastery` — Update status (`"mastered"` or `"learning"`)

### Learning Progress & Analytics
- `GET /api/progress/dashboard-stats` — Aggregates total docs, questions asked, quiz attempts, and syllabus progress

### Settings
- `GET /api/settings` — Get active LLM provider and ChromaDB vector store status
- `POST /api/settings/keys` — Update Anthropic Claude / OpenAI API keys

Interactive Swagger UI documentation is available at: **`http://127.0.0.1:8000/docs`**

---

## 🚢 Deployment Guide

### Frontend Deployment (Vercel)
1. Push the repository to GitHub.
2. In Vercel, import the repo and set:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variable**: `VITE_API_URL=https://your-backend-render-app.onrender.com/api`

### Backend Deployment (Render)
1. In Render, create a new **Web Service**.
2. Connect your GitHub repository.
3. Configure:
   - **Root Directory**: `backend` (or leave root and set start command)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Set environment variables:
   - `SECRET_KEY`: (Secure random string)
   - `DATABASE_URL`: (PostgreSQL URL or SQLite)
   - `ANTHROPIC_API_KEY`: (Optional)

---

## 🎓 Academic Integrity & Hallucination Mitigation Note

StudyMate AI employs strict prompt-engineering guardrails and dense vector relevance thresholds. When an inquiry falls outside the uploaded syllabus, the assistant explicitly alerts the student rather than synthesizing ungrounded assertions. Every proposition is linked to verified page metadata.
