import React, { useState } from 'react';
import { BookOpen, Mail, ArrowLeft, CheckCircle2, AlertCircle, Loader2, Send } from 'lucide-react';
import { api } from '../api';
import { useToast } from '../context/ToastContext';

export default function ForgotPasswordPage({ onNavigateLogin, onNavigateHome }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.forgotPassword(email);
      setSubmitted(true);
      toast.success('Password recovery instructions dispatched.');
    } catch (err) {
      toast.error(err.message || 'Failed to submit recovery request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 selection:bg-indigo-100 animate-fadeIn">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <button
          onClick={onNavigateHome}
          className="flex items-center justify-center gap-2.5 mx-auto group mb-4"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-purple-600 flex items-center justify-center text-white shadow-md shadow-indigo-200">
            <BookOpen className="w-5 h-5" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-xl font-extrabold text-slate-900 tracking-tight">StudyMate</span>
            <span className="px-1.5 py-0.5 text-xs font-bold bg-indigo-100 text-indigo-700 rounded-md">AI</span>
          </div>
        </button>

        <h2 className="text-center text-2xl font-extrabold text-slate-900 tracking-tight">
          Reset Your Password
        </h2>
        <p className="mt-1 text-center text-xs text-slate-500">
          Enter your registered student email to receive recovery instructions.
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 sm:px-10 rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-200/50 space-y-5">
          {submitted ? (
            <div className="text-center space-y-4 py-4 animate-scaleUp">
              <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-sm font-bold text-slate-900">Recovery Instructions Sent</h3>
              <p className="text-xs text-slate-500 leading-relaxed max-w-xs mx-auto">
                If an account exists for <span className="font-semibold text-slate-800">{email}</span>, check your inbox for the reset link.
              </p>
              <button
                type="button"
                onClick={onNavigateLogin}
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm transition"
              >
                Back to Sign In
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="student@studymate.ai"
                    className="w-full pl-10 pr-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 text-white text-xs sm:text-sm font-bold shadow-md shadow-indigo-200 transition flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                <span>{loading ? 'Sending Instructions...' : 'Send Recovery Link'}</span>
              </button>

              <button
                type="button"
                onClick={onNavigateLogin}
                className="w-full py-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-600 text-xs font-bold transition flex items-center justify-center gap-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Return to Sign In</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
