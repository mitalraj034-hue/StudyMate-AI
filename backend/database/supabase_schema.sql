-- ==============================================================================
-- STUDYMATE AI - SUPABASE CLOUD POSTGRESQL & PGVECTOR MIGRATION SCHEMA
-- ==============================================================================
-- Description: Complete relational schema with pgvector similarity search,
-- Supabase Storage configuration, Row Level Security (RLS) policies, and cascading constraints.
-- ==============================================================================

-- 1. Enable Required PostgreSQL Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    major TEXT DEFAULT 'General Studies',
    target_exam TEXT DEFAULT 'Semester Exams',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

-- Index for fast user authentication lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- 3. Documents Table (Metadata for PDFs stored in Supabase Storage)
CREATE TABLE IF NOT EXISTS public.documents (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    storage_path TEXT, -- Reference to file object in Supabase Storage bucket 'documents'
    file_size INTEGER DEFAULT 0,
    page_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'processing', -- 'uploading', 'processing', 'completed', 'failed'
    summary TEXT,
    key_points_json JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);

-- 4. Document Chunks Table with pgvector Dense Embeddings (Gemini 768-dim)
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768), -- Dense vector embeddings from Gemini text-embedding-004
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON public.document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_page_number ON public.document_chunks(document_id, page_number);

-- Vector Index for Sub-Millisecond Cosine Similarity Search
-- (HNSW index for high-precision nearest-neighbor retrieval)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
ON public.document_chunks USING hnsw (embedding vector_cosine_ops);

-- 5. Chat Sessions & Chat Messages / Chat History
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    title TEXT DEFAULT 'Study Session',
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id BIGINT REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    citations JSONB DEFAULT '[]'::jsonb, -- Array of {page_number, excerpt, relevance_score}
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    citations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chat_history_user_doc ON public.chat_history(user_id, document_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_doc ON public.chat_messages(document_id);

-- 6. Summaries Table
CREATE TABLE IF NOT EXISTS public.summaries (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    executive_summary TEXT NOT NULL,
    key_concepts JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_summaries_document_id ON public.summaries(document_id);

-- 7. Quizzes and Quiz Questions
CREATE TABLE IF NOT EXISTS public.quizzes (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    difficulty TEXT DEFAULT 'Medium',
    total_questions INTEGER DEFAULT 5,
    questions_json JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.quiz_questions (
    id BIGSERIAL PRIMARY KEY,
    quiz_id BIGINT REFERENCES public.quizzes(id) ON DELETE CASCADE NOT NULL,
    question_index INTEGER NOT NULL,
    question TEXT NOT NULL,
    options JSONB NOT NULL, -- ['Option A', 'Option B', 'Option C', 'Option D']
    correct_answer_index INTEGER NOT NULL,
    explanation TEXT,
    page_number INTEGER,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.quiz_results (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    quiz_id BIGINT REFERENCES public.quizzes(id) ON DELETE CASCADE,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    wrong_answers INTEGER NOT NULL,
    score INTEGER NOT NULL,
    percentage NUMERIC(5, 2) NOT NULL,
    answers_json JSONB DEFAULT '{}'::jsonb,
    time_spent_seconds INTEGER DEFAULT 60,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.quiz_answers (
    id BIGSERIAL PRIMARY KEY,
    attempt_id BIGINT REFERENCES public.quiz_results(id) ON DELETE CASCADE NOT NULL,
    question_index INTEGER,
    user_choice INTEGER,
    is_correct BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_quiz_results_user ON public.quiz_results(user_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_document ON public.quizzes(document_id);
CREATE INDEX IF NOT EXISTS idx_quiz_answers_attempt ON public.quiz_answers(attempt_id);

-- 8. Flashcards
CREATE TABLE IF NOT EXISTS public.flashcard_sets (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    title TEXT NOT NULL,
    total_cards INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.flashcards (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    document_id BIGINT REFERENCES public.documents(id) ON DELETE CASCADE NOT NULL,
    set_id BIGINT REFERENCES public.flashcard_sets(id) ON DELETE SET NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    topic TEXT,
    page_number INTEGER DEFAULT 1,
    status TEXT DEFAULT 'new', -- 'new', 'learning', 'mastered', 'known', 'review'
    mastery_status TEXT DEFAULT 'learning',
    times_reviewed INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.flashcard_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    flashcard_id BIGINT REFERENCES public.flashcards(id) ON DELETE CASCADE NOT NULL,
    mastery_status TEXT DEFAULT 'learning',
    review_count INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_flashcards_user_doc ON public.flashcards(user_id, document_id);
CREATE INDEX IF NOT EXISTS idx_flashcard_progress_user ON public.flashcard_progress(user_id, flashcard_id);

-- 9. Activity Logs (For Real-time Student Learning Velocity Dashboard)
CREATE TABLE IF NOT EXISTS public.activity_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    activity_type TEXT NOT NULL, -- 'upload', 'chat', 'quiz', 'flashcard', 'summary'
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON public.activity_logs(user_id, created_at DESC);

-- ==============================================================================
-- 10. SUPABASE VECTOR SEARCH RPC FUNCTION (pgvector Cosine Distance)
-- ==============================================================================
CREATE OR REPLACE FUNCTION match_document_chunks (
    query_embedding vector(768),
    filter_document_id BIGINT,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    chunk_index INT,
    page_number INT,
    content TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.page_number,
        dc.content,
        ROUND((1.0 - (dc.embedding <=> query_embedding))::numeric, 4)::float AS similarity
    FROM public.document_chunks dc
    WHERE dc.document_id = filter_document_id
      AND dc.embedding IS NOT NULL
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ==============================================================================
-- 11. SUPABASE STORAGE BUCKET CONFIGURATION
-- ==============================================================================
-- Ensure the 'documents' bucket exists in Supabase Storage
INSERT INTO storage.buckets (id, name, public) 
VALUES ('documents', 'documents', false)
ON CONFLICT (id) DO NOTHING;

-- ==============================================================================
-- 12. ROW LEVEL SECURITY (RLS) POLICIES
-- ==============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcard_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcard_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;

-- Allow backend service role key full access to all tables
DO $$
BEGIN
    EXECUTE 'CREATE POLICY service_role_all_users ON public.users FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_documents ON public.documents FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_chunks ON public.document_chunks FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_chat ON public.chat_history FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_summaries ON public.summaries FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_quizzes ON public.quizzes FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_quiz_results ON public.quiz_results FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_quiz_answers ON public.quiz_answers FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_flashcard_sets ON public.flashcard_sets FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_flashcards ON public.flashcards FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_flashcard_progress ON public.flashcard_progress FOR ALL TO service_role USING (true) WITH CHECK (true)';
    EXECUTE 'CREATE POLICY service_role_all_activity ON public.activity_logs FOR ALL TO service_role USING (true) WITH CHECK (true)';
EXCEPTION WHEN OTHERS THEN
    -- Policies already created
    NULL;
END $$;
