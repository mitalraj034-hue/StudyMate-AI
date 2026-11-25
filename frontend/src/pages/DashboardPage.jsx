import React, { useState, useEffect } from 'react';
import {
  FileText,
  MessageSquare,
  HelpCircle,
  TrendingUp,
  Layers,
  ArrowRight,
  Upload,
  Sparkles,
  Clock,
  Award,
  ChevronRight,
  BookOpen,
  CheckCircle2,
  Calendar,
  Zap,
  BarChart2
} from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage({ setActiveTab, onOpenUpload, setActiveDocId }) {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const metrics = stats?.metrics || {
    total_documents: 0,
    questions_asked: 0,
    quizzes_completed: 0,
    avg_quiz_score: 0,
    study_progress: 0,
    flashcards_total: 0,
    flashcards_mastered: 0
  };

  const statCards = [
    {
      label: 'Total Documents',
      value: metrics.total_documents,
      detail: 'Indexed in ChromaDB',
      icon: FileText,
      gradient: 'from-blue-600 to-indigo-600',
      bgLight: 'bg-blue-50 text-blue-600'
    },
    {
      label: 'Questions Asked',
      value: metrics.questions_asked,
      detail: 'Grounded RAG answers',
      icon: MessageSquare,
      gradient: 'from-purple-600 to-pink-600',
      bgLight: 'bg-purple-50 text-purple-600'
    },
    {
      label: 'Quizzes Completed',
      value: metrics.quizzes_completed,
      detail: 'Practice exam sets',
      icon: HelpCircle,
      gradient: 'from-amber-500 to-orange-600',
      bgLight: 'bg-amber-50 text-amber-600'
    },
    {
      label: 'Average Quiz Score',
      value: `${metrics.avg_quiz_score}%`,
      detail: 'Performance rating',
      icon: Award,
      gradient: 'from-emerald-500 to-teal-600',
      bgLight: 'bg-emerald-50 text-emerald-600'
    },
    {
      label: 'Course Mastery',
      value: `${metrics.study_progress}%`,
      detail: 'Syllabus completion',
      icon: TrendingUp,
      gradient: 'from-indigo-600 to-purple-600',
      bgLight: 'bg-indigo-50 text-indigo-600'
    }
  ];

  const handleDocClick = (docId, tab) => {
    if (setActiveDocId) setActiveDocId(docId);
    setActiveTab(tab);
  };

  const displayName = user?.name || user?.full_name || 'Student';
  const recentDocs = stats?.recent_documents || [];
  const recentScores = stats?.recent_quiz_scores || [];
  const recentActivities = stats?.recent_activities || [];
  const continueDoc = recentDocs.length > 0 ? recentDocs[0] : null;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 text-white relative overflow-hidden shadow-xl animate-fadeIn">
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-white/10 to-transparent pointer-events-none" />
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-indigo-200 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5 text-indigo-300" />
            <span>AI-Powered Academic Workspace</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {displayName} 👋
          </h2>

          <p className="mt-2 text-xs sm:text-sm text-indigo-100/90 leading-relaxed font-normal">
            Target Goal: <span className="font-semibold text-white">{user?.target_exam || 'Semester Finals'}</span> • Track: <span className="font-semibold text-white">{user?.major || 'General Studies'}</span>.
            Your course documents are chunked and ready for zero-hallucination inquiries.
          </p>

          <div className="mt-5 flex flex-wrap gap-2.5">
            <button
              onClick={onOpenUpload}
              className="px-4 py-2 rounded-xl bg-white text-indigo-900 hover:bg-slate-100 text-xs font-bold shadow-md transition flex items-center gap-1.5"
            >
              <Upload className="w-3.5 h-3.5" />
              <span>Upload New PDF</span>
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className="px-4 py-2 rounded-xl bg-indigo-700/60 hover:bg-indigo-700 border border-indigo-400/30 text-white text-xs font-bold transition flex items-center gap-1.5"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ask AI Chat</span>
            </button>
            <button
              onClick={() => setActiveTab('quiz')}
              className="px-4 py-2 rounded-xl bg-indigo-700/60 hover:bg-indigo-700 border border-indigo-400/30 text-white text-xs font-bold transition flex items-center gap-1.5"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Take Quiz</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Statistics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((sc, i) => {
          const Icon = sc.icon;
          return (
            <div
              key={i}
              className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-500">{sc.label}</span>
                <div className={`p-2 rounded-xl ${sc.bgLight}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div>
                <p className="text-2xl font-extrabold text-slate-900 tracking-tight">{sc.value}</p>
                <p className="text-[11px] text-slate-400 mt-0.5">{sc.detail}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Continue Studying Highlight Section */}
      {continueDoc && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100/90 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-white border border-indigo-200 shadow-sm flex items-center justify-center text-indigo-600 shrink-0">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-0.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-indigo-100 text-indigo-700">
                  Continue Reading
                </span>
                <span className="text-xs text-slate-400 font-medium">
                  {continueDoc.pages} Pages • {continueDoc.chunks} Vector Chunks
                </span>
              </div>
              <h3 className="text-sm sm:text-base font-bold text-slate-900 truncate max-w-lg">
                {continueDoc.original_filename || continueDoc.name}
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => handleDocClick(continueDoc.id, 'chat')}
              className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm transition flex items-center justify-center gap-1.5"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Resume Chat</span>
            </button>
            <button
              onClick={() => handleDocClick(continueDoc.id, 'quiz')}
              className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-bold transition flex items-center justify-center gap-1.5"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Practice Quiz</span>
            </button>
          </div>
        </div>
      )}

      {/* Two Column Layout: Recent Documents & Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Study Materials */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-600" />
              <span>Recent Study Materials</span>
            </h3>
            <button
              onClick={() => setActiveTab('documents')}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              <span>View All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {recentDocs.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-2xl border border-slate-200/80 shadow-xs">
              <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs font-semibold text-slate-600">No documents uploaded yet</p>
              <button
                onClick={onOpenUpload}
                className="mt-3 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-xl transition"
              >
                Upload First Course PDF
              </button>
            </div>
          ) : (
            <div className="space-y-2.5">
              {recentDocs.map((doc) => (
                <div
                  key={doc.id}
                  className="p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-indigo-200 hover:shadow-sm transition flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 shrink-0">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div className="overflow-hidden">
                      <h4 className="text-xs font-bold text-slate-900 truncate max-w-sm">
                        {doc.original_filename || doc.name}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {doc.pages || 0} pages • {doc.chunks || 0} vector chunks
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 self-end sm:self-center shrink-0">
                    <button
                      onClick={() => handleDocClick(doc.id, 'chat')}
                      className="px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 transition"
                      title="AI Chat"
                    >
                      Chat
                    </button>
                    <button
                      onClick={() => handleDocClick(doc.id, 'quiz')}
                      className="px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-700 transition"
                      title="Generate Quiz"
                    >
                      Quiz
                    </button>
                    <button
                      onClick={() => handleDocClick(doc.id, 'flashcards')}
                      className="px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 transition"
                      title="Flashcards"
                    >
                      Cards
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Recent Scores & Activity */}
        <div className="space-y-6">
          {/* Recent Quiz Scores */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-500" />
              <span>Recent Quiz Scores</span>
            </h3>

            {recentScores.length === 0 ? (
              <div className="p-5 text-center bg-white rounded-2xl border border-slate-200/80 shadow-xs">
                <p className="text-xs text-slate-400">No quizzes taken yet.</p>
                <button
                  onClick={() => setActiveTab('quiz')}
                  className="mt-2 text-xs font-bold text-indigo-600 hover:underline"
                >
                  Generate a quiz
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {recentScores.map((score, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-white border border-slate-200/80 shadow-2xs flex items-center justify-between"
                  >
                    <div className="overflow-hidden">
                      <p className="text-xs font-bold text-slate-800 truncate">{score.quiz_title || score.document_name}</p>
                      <p className="text-[10px] text-slate-400">{score.completed_at?.split('T')[0] || 'Recent'}</p>
                    </div>
                    <span
                      className={`text-xs font-extrabold px-2.5 py-1 rounded-full ${
                        score.percentage >= 75
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : score.percentage >= 50
                          ? 'bg-amber-50 text-amber-700 border border-amber-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}
                    >
                      {score.score}/{score.total_questions} ({score.percentage}%)
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Activity Stream */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-600" />
              <span>Recent Study Activity</span>
            </h3>

            <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
              {recentActivities.length === 0 ? (
                <p className="text-xs text-slate-400 text-center py-2">No activity recorded yet.</p>
              ) : (
                recentActivities.slice(0, 4).map((act, i) => (
                  <div key={i} className="flex items-start gap-3 text-xs pb-2 border-b border-slate-100 last:border-0 last:pb-0">
                    <div className="w-2 h-2 rounded-full bg-indigo-600 mt-1.5 shrink-0" />
                    <div>
                      <p className="font-bold text-slate-800">{act.title}</p>
                      <p className="text-[11px] text-slate-400 leading-tight mt-0.5">{act.description}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
