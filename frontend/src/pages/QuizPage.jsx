import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  Sparkles,
  CheckCircle2,
  XCircle,
  ArrowRight,
  ArrowLeft,
  RotateCcw,
  Clock,
  Award,
  BookOpen,
  FileText,
  Loader2,
  ChevronRight,
  Sliders,
  Filter
} from 'lucide-react';
import { api } from '../api';
import CitationBadge from '../components/CitationBadge';
import { useToast } from '../context/ToastContext';

export default function QuizPage({ activeDocId, documents = [] }) {
  const [quizzes, setQuizzes] = useState([]);
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [difficulty, setDifficulty] = useState('Medium');
  const [questionCount, setQuestionCount] = useState(5);
  const [customTopic, setCustomTopic] = useState('');
  const toast = useToast();

  const selectedDoc = documents.find((d) => d.id === Number(activeDocId));

  const loadQuizzes = async () => {
    if (!activeDocId) return;
    try {
      const data = await api.getQuizzesForDocument(activeDocId);
      setQuizzes(data);
      if (data.length > 0) {
        loadQuizDetails(data[0].id);
      } else {
        setActiveQuiz(null);
        setQuizResult(null);
      }
    } catch (err) {
      console.error('Failed to load quizzes:', err);
    }
  };

  const loadQuizDetails = async (quizId) => {
    try {
      const quiz = await api.getQuiz(quizId);
      setActiveQuiz(quiz);
      setCurrentQuestionIndex(0);
      setSelectedAnswers({});
      setQuizResult(null);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load quiz questions');
    }
  };

  useEffect(() => {
    loadQuizzes();
  }, [activeDocId]);

  const handleGenerateQuiz = async () => {
    if (!activeDocId) return;
    setGenerating(true);
    try {
      const topicParam = customTopic.trim() ? customTopic.trim() : null;
      const newQuiz = await api.generateQuiz(
        activeDocId,
        questionCount,
        difficulty,
        null,
        topicParam
      );
      toast.success(`Generated ${newQuiz.total_questions || questionCount} MCQ questions via Gemini!`);
      setQuizzes((prev) => [newQuiz, ...prev]);
      setActiveQuiz(newQuiz);
      setCurrentQuestionIndex(0);
      setSelectedAnswers({});
      setQuizResult(null);
    } catch (err) {
      toast.error(err.message || 'Failed to generate quiz.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSelectOption = (questionId, optionIndex) => {
    if (quizResult) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [String(questionId)]: optionIndex
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);
    try {
      const result = await api.submitQuiz(activeQuiz.id, selectedAnswers);
      setQuizResult(result);
      toast.success(`Quiz graded: ${result.score}/${result.total_questions} (${result.percentage}%)`);
    } catch (err) {
      toast.error(err.message || 'Failed to submit quiz.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!selectedDoc) {
    return (
      <div className="p-12 text-center bg-white rounded-3xl border border-slate-200/80 shadow-sm max-w-xl mx-auto mt-10">
        <HelpCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-800">No Document Selected</h3>
        <p className="text-xs text-slate-500 mt-1">Please select or upload a document to practice MCQ exam questions.</p>
      </div>
    );
  }

  const questions = activeQuiz?.questions || [];
  const currentQ = questions[currentQuestionIndex];
  const progressPercent = questions.length > 0 ? Math.round(((currentQuestionIndex + 1) / questions.length) * 100) : 0;
  const answeredCount = Object.keys(selectedAnswers).length;

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fadeIn">
      {/* Quiz Top Action & Generator Bar */}
      <div className="bg-white p-5 sm:p-6 rounded-3xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 text-[10px] font-bold uppercase tracking-wider">
              Gemini Dynamic Exam Generator
            </span>
            <span className="text-xs text-slate-400">
              {selectedDoc.original_filename || selectedDoc.original_name}
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
            MCQ Assessment & Knowledge Evaluation
          </h2>
        </div>

        {/* Generator Controls */}
        <div className="flex flex-wrap items-center gap-2 self-stretch md:self-center">
          <input
            type="text"
            value={customTopic}
            onChange={(e) => setCustomTopic(e.target.value)}
            placeholder="Focus Topic / Chapter (Optional)"
            className="px-3 py-1.5 text-xs font-medium rounded-xl bg-slate-50 border border-slate-200 text-slate-700 outline-none w-full sm:w-48 placeholder:text-slate-400"
          />

          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-50 border border-slate-200 text-slate-700 outline-none cursor-pointer"
          >
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>

          <select
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-50 border border-slate-200 text-slate-700 outline-none cursor-pointer"
          >
            <option value={3}>3 Questions</option>
            <option value={5}>5 Questions</option>
            <option value={8}>8 Questions</option>
            <option value={10}>10 Questions</option>
            <option value={15}>15 Questions</option>
            <option value={20}>20 Questions</option>
          </select>

          <button
            onClick={handleGenerateQuiz}
            disabled={generating}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-1.5 shrink-0"
          >
            {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>{generating ? 'Generating...' : 'New Quiz'}</span>
          </button>
        </div>
      </div>

      {/* Main Quiz Area: Active Exam Player OR Result Screen */}
      {!activeQuiz || questions.length === 0 ? (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mx-auto shadow-xs">
            <HelpCircle className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">No Quizzes Generated Yet</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto leading-relaxed">
              Click "New Quiz" above to automatically generate multiple-choice questions dynamically grounded in this document with Google Gemini.
            </p>
          </div>
          <button
            onClick={handleGenerateQuiz}
            disabled={generating}
            className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-orange-600 text-white text-xs font-bold rounded-xl shadow-md transition inline-flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate First Quiz</span>
          </button>
        </div>
      ) : quizResult ? (
        /* Results View */
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm space-y-6 animate-scaleUp">
          {/* Result Score Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-900 to-purple-900 text-white flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
            <div>
              <span className="px-2.5 py-0.5 rounded-full bg-white/10 text-indigo-200 text-xs font-semibold">
                Exam Evaluation Completed
              </span>
              <h3 className="text-2xl font-extrabold mt-1">
                {quizResult.percentage >= 75 ? '🎉 Outstanding Performance!' : quizResult.percentage >= 50 ? '👍 Solid Effort!' : '📚 Review Required'}
              </h3>
              <p className="text-xs text-indigo-200 mt-1">
                You scored <span className="font-bold text-white">{quizResult.score}</span> out of <span className="font-bold text-white">{quizResult.total_questions}</span> questions ({quizResult.percentage}% accuracy).
              </p>
            </div>

            <div className="w-20 h-20 rounded-full border-4 border-emerald-400 bg-white/10 flex flex-col items-center justify-center shrink-0">
              <span className="text-xl font-black text-white">{quizResult.percentage}%</span>
              <span className="text-[10px] text-indigo-200 font-bold uppercase tracking-wider">Score</span>
            </div>
          </div>

          {/* Question Breakdown List */}
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-slate-900">Detailed Answer Review & Verified Provenance</h4>

            {quizResult.feedback?.map((fb, idx) => (
              <div
                key={fb.id || idx}
                className={`p-5 rounded-2xl border ${
                  fb.is_correct
                    ? 'bg-emerald-50/40 border-emerald-200/80'
                    : 'bg-rose-50/40 border-rose-200/80'
                } space-y-3`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2.5">
                    {fb.is_correct ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <span className="text-xs font-extrabold text-slate-500 block mb-0.5">Question {idx + 1}</span>
                      <h5 className="text-xs sm:text-sm font-bold text-slate-900 leading-snug">{fb.question}</h5>
                    </div>
                  </div>

                  {fb.page_number && (
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 shrink-0">
                      Page {fb.page_number}
                    </span>
                  )}
                </div>

                {/* Explanation text */}
                <div className="text-xs text-slate-700 bg-white/80 p-3 rounded-xl border border-slate-200/60 leading-relaxed">
                  <span className="font-bold text-slate-900">Explanation: </span>
                  {fb.explanation || 'Verified from course reading.'}
                </div>
              </div>
            ))}
          </div>

          {/* Result Actions */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <button
              onClick={() => {
                setQuizResult(null);
                setCurrentQuestionIndex(0);
                setSelectedAnswers({});
              }}
              className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retake This Quiz</span>
            </button>

            <button
              onClick={handleGenerateQuiz}
              disabled={generating}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm transition flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Generate Another Quiz</span>
            </button>
          </div>
        </div>
      ) : (
        /* Active Exam Simulator View */
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-sm space-y-6">
          {/* Progress Header */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500">
              <div className="flex items-center gap-2">
                <span>Question {currentQuestionIndex + 1} of {questions.length}</span>
                {activeQuiz.topic && activeQuiz.topic !== 'General Syllabus' && (
                  <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 text-[10px] font-bold border border-amber-200">
                    Topic: {activeQuiz.topic}
                  </span>
                )}
              </div>
              <span>{answeredCount}/{questions.length} Answered</span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-300 rounded-full"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* Question Card */}
          {currentQ && (
            <div className="space-y-5">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-sm sm:text-base font-extrabold text-slate-900 leading-snug">
                  {currentQ.question}
                </h3>
                {currentQ.page_number && (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200 shrink-0">
                    Page {currentQ.page_number}
                  </span>
                )}
              </div>

              {/* Options A, B, C, D */}
              <div className="space-y-2.5">
                {currentQ.options?.map((opt, optIdx) => {
                  const letter = String.fromCharCode(65 + optIdx);
                  const isSelected = selectedAnswers[String(currentQ.id)] === optIdx;

                  return (
                    <button
                      key={optIdx}
                      onClick={() => handleSelectOption(currentQ.id, optIdx)}
                      className={`w-full p-4 rounded-2xl border text-left transition-all duration-150 flex items-center gap-3.5 ${
                        isSelected
                          ? 'border-indigo-600 bg-indigo-50/70 shadow-xs'
                          : 'border-slate-200/80 hover:border-slate-300 hover:bg-slate-50/60'
                      }`}
                    >
                      <span
                        className={`w-7 h-7 rounded-xl text-xs font-extrabold flex items-center justify-center shrink-0 ${
                          isSelected
                            ? 'bg-indigo-600 text-white'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {letter}
                      </span>
                      <span className="text-xs sm:text-sm font-medium text-slate-800 leading-relaxed">
                        {opt}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Navigation Controls */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <button
              onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentQuestionIndex === 0}
              className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 disabled:opacity-40 text-slate-700 text-xs font-bold transition flex items-center gap-1.5"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Previous</span>
            </button>

            {currentQuestionIndex < questions.length - 1 ? (
              <button
                onClick={() => setCurrentQuestionIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white text-xs font-bold transition flex items-center gap-1.5"
              >
                <span>Next</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                onClick={handleSubmitQuiz}
                disabled={submitting}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 disabled:opacity-50 text-white text-xs font-extrabold shadow-md transition flex items-center gap-1.5"
              >
                {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                <span>Submit Exam</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}