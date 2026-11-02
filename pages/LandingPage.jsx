import React, { useState } from 'react';
import {
  BookOpen,
  ArrowRight,
  FileText,
  MessageSquare,
  Sparkles,
  HelpCircle,
  Layers,
  TrendingUp,
  ShieldCheck,
  Cpu,
  CheckCircle2,
  FileCheck,
  ChevronRight,
  Zap,
  Award,
  Upload,
  ExternalLink,
  Lock
} from 'lucide-react';

export default function LandingPage({ onNavigateLogin, onNavigateRegister, onDemoLogin }) {
  const [activeWorkflowStep, setActiveWorkflowStep] = useState(0);

  const workflowSteps = [
    {
      step: '01',
      title: 'Upload Course PDF',
      desc: 'Drag and drop course notes, textbooks, slides, or syllabus readings up to 25MB.',
      icon: Upload,
      badge: 'Page-by-page OCR'
    },
    {
      step: '02',
      title: 'Semantic Vector Indexing',
      desc: 'Chunks are indexed in ChromaDB vector storage with dense embeddings and page provenance.',
      icon: Cpu,
      badge: 'Dense Vectors'
    },
    {
      step: '03',
      title: 'Inquire with Strict Grounding',
      desc: 'Ask complex academic questions and get answers grounded strictly in retrieved passages.',
      icon: MessageSquare,
      badge: 'Zero Hallucination'
    },
    {
      step: '04',
      title: 'Test with Adaptive Quizzes',
      desc: 'Generate targeted MCQ exams with instant grading, explanations, and page citations.',
      icon: HelpCircle,
      badge: 'Auto Grading'
    },
    {
      step: '05',
      title: 'Master via Active Recall',
      desc: 'Practice 3D flip flashcards and track syllabus completion on your personal dashboard.',
      icon: Layers,
      badge: '3D Memory Deck'
    }
  ];

  const features = [
    {
      title: 'PDF Intelligence',
      desc: 'Deep page-by-page text extraction preserves exact page numbers and layout hierarchy for every excerpt.',
      icon: FileText,
      tag: 'Multi-Page Extraction',
      gradient: 'from-blue-600 to-indigo-600'
    },
    {
      title: 'Grounded AI Chat',
      desc: 'Inquire directly with your syllabus. AI synthesizes clear answers strictly from retrieved course material.',
      icon: MessageSquare,
      tag: 'Zero Hallucination',
      gradient: 'from-indigo-600 to-purple-600'
    },
    {
      title: 'Smart Summaries',
      desc: 'Distill 50-page lecture notes into structured executive overviews, key concepts, and quick exam bullet points.',
      icon: Sparkles,
      tag: 'Instant Revision',
      gradient: 'from-purple-600 to-pink-600'
    },
    {
      title: 'MCQ Quiz Generator',
      desc: 'Auto-generate practice exams with options A/B/C/D, real-time grading, and verified page-wise explanations.',
      icon: HelpCircle,
      tag: 'Adaptive Testing',
      gradient: 'from-pink-600 to-rose-600'
    },
    {
      title: '3D Active Recall Flashcards',
      desc: 'Interactive 3D flip study cards to memorize critical terms, formulas, and definitions at your pace.',
      icon: Layers,
      tag: 'Memory Retention',
      gradient: 'from-amber-500 to-orange-600'
    },
    {
      title: 'Learning Analytics',
      desc: 'Visualize your quiz performance trends, study progress, document mastery, and exam readiness scores.',
      icon: TrendingUp,
      tag: 'Performance Tracking',
      gradient: 'from-emerald-500 to-teal-600'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      {/* SaaS Navigation Header */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-200">
              <BookOpen className="w-5 h-5" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-xl text-slate-900 tracking-tight">StudyMate</span>
              <span className="px-1.5 py-0.5 text-xs font-bold bg-indigo-100 text-indigo-700 rounded-md">AI</span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold text-slate-600">
            <a href="#features" className="hover:text-indigo-600 transition">Features</a>
            <a href="#workflow" className="hover:text-indigo-600 transition">How It Works</a>
            <a href="#rag" className="hover:text-indigo-600 transition">Grounded RAG</a>
            <a href="#preview" className="hover:text-indigo-600 transition">Live Preview</a>
          </nav>

          {/* Header Action Buttons */}
          <div className="flex items-center gap-3">
            <button
              onClick={onDemoLogin}
              className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-xl transition"
            >
              <Zap className="w-3.5 h-3.5 text-indigo-600 fill-indigo-600" />
              <span>Instant Demo</span>
            </button>

            <button
              onClick={onNavigateLogin}
              className="px-4 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 transition"
            >
              Sign In
            </button>

            <button
              onClick={onNavigateRegister}
              className="px-4 py-2 text-xs font-bold text-white bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 rounded-xl shadow-md shadow-indigo-200 transition transform hover:-translate-y-0.5"
            >
              Get Started Free
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-32 overflow-hidden">
        {/* Subtle decorative background gradient */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-gradient-to-tr from-indigo-300/30 via-purple-300/20 to-pink-200/30 blur-3xl -z-10 rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Academic Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 border border-indigo-200/90 text-indigo-700 text-xs font-semibold mb-6 shadow-xs animate-fadeIn">
            <ShieldCheck className="w-4 h-4 text-indigo-600" />
            <span>Retrieval-Augmented Generation with Verified Page Citations</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-950 tracking-tight leading-[1.15] max-w-4xl mx-auto">
            Study Smarter. Learn Faster. <br />
            <span className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 bg-clip-text text-transparent">
              With StudyMate AI.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 text-sm sm:text-base md:text-lg text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
            AI-powered document study assistant with grounded answers, page citations, quizzes, and flashcards. Upload your course syllabus to eliminate hallucinations and master your exams.
          </p>

          {/* Action CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <button
              onClick={onNavigateRegister}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white text-sm font-bold shadow-lg shadow-indigo-200 flex items-center justify-center gap-2 transition transform hover:-translate-y-0.5"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={onDemoLogin}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-800 text-sm font-bold shadow-xs flex items-center justify-center gap-2 transition"
            >
              <Zap className="w-4 h-4 text-indigo-600" />
              <span>Explore Demo Account</span>
            </button>
          </div>

          {/* Security & Feature Badges */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-6 sm:gap-10 text-xs font-semibold text-slate-500">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Zero Hallucinations</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Exact Page Citations</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>ChromaDB Vector Retrieval</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>PostgreSQL Reliability</span>
            </div>
          </div>
        </div>

        {/* Live Interactive UI Preview Mockup */}
        <div id="preview" className="mt-16 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl bg-white border border-slate-200/90 shadow-2xl p-4 sm:p-6 lg:p-8">
            {/* Mock Header */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <div className="w-3 h-3 rounded-full bg-rose-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="ml-2 text-xs font-semibold text-slate-400">StudyMate AI Grounded Workspace</span>
              </div>
              <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                ● 100% Citation Grounded
              </span>
            </div>

            {/* Mock Chat & Citation Display */}
            <div className="py-6 space-y-4">
              {/* User Inquiry */}
              <div className="flex justify-end">
                <div className="max-w-lg bg-indigo-600 text-white p-4 rounded-2xl rounded-tr-none text-xs sm:text-sm leading-relaxed shadow-sm">
                  What are the foundational stages of the Retrieval-Augmented Generation pipeline?
                </div>
              </div>

              {/* AI Grounded Response */}
              <div className="flex justify-start">
                <div className="max-w-2xl bg-slate-50 border border-slate-200/80 p-5 rounded-2xl rounded-tl-none text-xs sm:text-sm text-slate-800 space-y-3 shadow-xs">
                  <div className="flex items-center gap-2 font-bold text-indigo-700 text-xs">
                    <Sparkles className="w-4 h-4" />
                    <span>StudyMate Assistant</span>
                  </div>
                  <p className="leading-relaxed">
                    According to your uploaded study material, the Retrieval-Augmented Generation (RAG) pipeline operates across three foundational stages:
                  </p>
                  <ol className="list-decimal pl-5 space-y-1 text-slate-700">
                    <li><strong>Document Chunking:</strong> Extracting text page-by-page and splitting it into semantically coherent overlapping segments.</li>
                    <li><strong>Dense Vector Embeddings:</strong> Encoding text chunks into high-dimensional numerical vectors.</li>
                    <li><strong>Cosine Similarity Retrieval:</strong> Querying the vector database (ChromaDB) to retrieve top-k chunks with page-level provenance.</li>
                  </ol>
                  <div className="pt-2 flex flex-wrap items-center gap-2 border-t border-slate-200/60">
                    <span className="text-xs font-semibold text-slate-500">Verified Sources:</span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
                      <BookOpen className="w-3 h-3" />
                      Page 4 · 96% match
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
                      <BookOpen className="w-3 h-3" />
                      Page 2 · 91% match
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Section */}
      <section id="features" className="py-20 bg-white border-y border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
              Complete Study Toolkit
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-3 tracking-tight">
              Everything You Need to Ace Your Courses
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-3">
              Purpose-built for college students, researchers, and exam candidates who need accurate answers backed by verified course citations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  className="p-6 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:bg-white hover:shadow-xl hover:border-indigo-200 transition-all duration-200 group"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${feat.gradient} flex items-center justify-center text-white shadow-md shadow-indigo-100 group-hover:scale-105 transition-transform`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-white text-slate-600 border border-slate-200 shadow-2xs">
                      {feat.tag}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                    {feat.title}
                  </h3>
                  <p className="mt-2 text-xs sm:text-sm text-slate-600 leading-relaxed">
                    {feat.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="workflow" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
              Interactive Workflow
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-3 tracking-tight">
              Upload → Ask → Learn → Test → Improve
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-3">
              How StudyMate AI turns dense course textbooks into verified learning velocity.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {workflowSteps.map((ws, i) => {
              const Icon = ws.icon;
              return (
                <div
                  key={i}
                  className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm flex flex-col justify-between hover:shadow-md transition"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-2xl font-black text-indigo-600/40">{ws.step}</span>
                      <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
                        <Icon className="w-4 h-4" />
                      </div>
                    </div>
                    <h4 className="font-bold text-slate-900 text-sm mb-1">{ws.title}</h4>
                    <p className="text-xs text-slate-500 leading-relaxed">{ws.desc}</p>
                  </div>
                  <span className="mt-4 inline-block text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 w-fit">
                    {ws.badge}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Ready to Study Banner */}
      <section className="py-16 bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
            Ready to Accelerate Your Academic Learning?
          </h2>
          <p className="text-indigo-200 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
            Join students studying smarter with document-grounded AI answers, verified citations, and active recall flashcards.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2">
            <button
              onClick={onNavigateRegister}
              className="w-full sm:w-auto px-7 py-3 rounded-xl bg-white text-indigo-900 hover:bg-slate-100 text-sm font-bold shadow-lg transition"
            >
              Create Free Account
            </button>
            <button
              onClick={onDemoLogin}
              className="w-full sm:w-auto px-7 py-3 rounded-xl bg-indigo-700/60 hover:bg-indigo-700 border border-indigo-400/30 text-white text-sm font-bold transition flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4" />
              <span>Launch Demo Account</span>
            </button>
          </div>
        </div>
      </section>

      {/* Professional SaaS Footer */}
      <footer className="bg-slate-950 text-slate-400 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold">
                <BookOpen className="w-4 h-4" />
              </div>
              <span className="font-extrabold text-lg text-white">StudyMate AI</span>
            </div>
            <div className="flex flex-wrap items-center gap-6 text-xs font-medium">
              <a href="#features" className="hover:text-white transition">Features</a>
              <a href="#workflow" className="hover:text-white transition">Workflow</a>
              <a href="/docs" target="_blank" className="hover:text-white transition">API Docs</a>
              <a href="#preview" className="hover:text-white transition">Grounded RAG</a>
              <button onClick={onNavigateLogin} className="hover:text-white transition">Student Login</button>
            </div>
          </div>
          <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
            <p>© 2026 StudyMate AI. All rights reserved. Academic Grounded Study Assistant.</p>
            <p>Built with FastAPI, React, PostgreSQL & ChromaDB.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
