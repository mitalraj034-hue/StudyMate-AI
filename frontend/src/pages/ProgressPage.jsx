import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  Award,
  BookOpen,
  HelpCircle,
  Layers,
  FileText,
  Clock,
  Sparkles,
  CheckCircle2,
  Calendar,
  Zap,
  BarChart2,
  ChevronRight
} from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function ProgressPage({ setActiveTab }) {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await api.getDashboardStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to load progress stats:', err);
        toast.error('Failed to load analytics');
      } finally {
        setLoading(false);
      }
    }
    loadStats();
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

  const recentScores = stats?.recent_quiz_scores || [];
  const recentActivities = stats?.recent_activities || [];
  const displayName = user?.name || user?.full_name || 'Student';

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fadeIn">
      {/* Top Analytics Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 text-white p-6 sm:p-8 rounded-3xl shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-indigo-200 text-xs font-semibold mb-2">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Academic Velocity & Exam Readiness</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Learning Progress & Mastery Trends
          </h2>
          <p className="text-xs sm:text-sm text-indigo-200/90 mt-1 max-w-xl">
            Student: <span className="font-bold text-white">{displayName}</span> • Target Exam: <span className="font-bold text-white">{user?.target_exam || 'Semester Finals'}</span>. Real-time metrics computed directly from database quiz results and grounded study activity.
          </p>
        </div>

        <div className="text-center md:text-right bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/20 shrink-0">
          <span className="text-4xl font-black text-emerald-400 block tracking-tight">
            {metrics.study_progress}%
          </span>
          <span className="text-[11px] text-indigo-200 uppercase tracking-wider font-bold">
            Course Mastery Gauge
          </span>
        </div>
      </div>

      {/* Analytics Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold text-slate-500">Average Exam Score</span>
            <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-extrabold text-slate-900">{metrics.avg_quiz_score}%</p>
            <div className="mt-2 w-full h-1.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full"
                style={{ width: `${metrics.avg_quiz_score}%` }}
              />
            </div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold text-slate-500">Quizzes Completed</span>
            <div className="p-2 rounded-xl bg-amber-50 text-amber-600">
              <HelpCircle className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-extrabold text-slate-900">{metrics.quizzes_completed}</p>
            <p className="text-[11px] text-slate-400 mt-1">Evaluated MCQ attempts</p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold text-slate-500">Flashcards Mastered</span>
            <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
              <Layers className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-extrabold text-slate-900">{metrics.flashcards_mastered || 0}</p>
            <p className="text-[11px] text-slate-400 mt-1">
              Out of {metrics.flashcards_total || 0} active recall cards
            </p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-bold text-slate-500">Questions Inquired</span>
            <div className="p-2 rounded-xl bg-purple-50 text-purple-600">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div>
            <p className="text-2xl font-extrabold text-slate-900">{metrics.questions_asked}</p>
            <p className="text-[11px] text-slate-400 mt-1">Zero-hallucination citations</p>
          </div>
        </div>
      </div>

      {/* Two Columns: Quiz Performance Breakdown & Activity Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Quiz Performance History */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-indigo-600" />
              <span>Exam Performance History</span>
            </h3>
            <button
              onClick={() => setActiveTab('quiz')}
              className="text-xs font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              <span>Take Quiz</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {recentScores.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-8">No quiz scores recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {recentScores.map((score, i) => (
                <div key={i} className="p-3.5 rounded-xl bg-slate-50/80 border border-slate-200/60 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-800 truncate max-w-[250px]">
                      {score.quiz_title || score.document_name}
                    </span>
                    <span className="font-extrabold text-indigo-600">
                      {score.score}/{score.total_questions} ({score.percentage}%)
                    </span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-slate-200 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        score.percentage >= 75 ? 'bg-emerald-500' : score.percentage >= 50 ? 'bg-amber-500' : 'bg-rose-500'
                      }`}
                      style={{ width: `${score.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Study Activity Audit Trail */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-600" />
              <span>Study Activity Stream</span>
            </h3>
            <span className="text-[11px] font-semibold text-slate-400">Live Audit</span>
          </div>

          {recentActivities.length === 0 ? (
            <p className="text-xs text-slate-400 text-center py-8">No study activity recorded yet.</p>
          ) : (
            <div className="space-y-3.5">
              {recentActivities.map((act, i) => (
                <div key={i} className="flex items-start gap-3 text-xs pb-3 border-b border-slate-100 last:border-0 last:pb-0">
                  <div className="w-2 h-2 rounded-full bg-indigo-600 mt-1.5 shrink-0" />
                  <div className="flex-1 overflow-hidden">
                    <p className="font-bold text-slate-800 truncate">{act.title}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{act.description}</p>
                  </div>
                  <span className="text-[10px] text-slate-400 shrink-0">
                    {act.created_at?.split('T')[0] || 'Today'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
