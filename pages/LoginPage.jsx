import React, { useState } from 'react';
import { BookOpen, Lock, Mail, ArrowRight, AlertCircle, Loader2, Sparkles, Zap, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

export default function LoginPage({ onNavigateRegister, onNavigateForgot, onNavigateHome }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      toast.success('Welcome back to StudyMate AI!');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
      toast.error('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = () => {
    setEmail('student@studymate.ai');
    setPassword('password123');
    setError(null);
    toast.info('Filled demo credentials: student@studymate.ai');
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
          Welcome back, Student
        </h2>
        <p className="mt-1 text-center text-xs text-slate-500">
          Sign in to access your course notes, grounded RAG inquiries, and quiz scores.
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 sm:px-10 rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-200/50 space-y-5">
          {/* Quick Demo Credentials Pill */}
          <button
            type="button"
            onClick={handleFillDemo}
            className="w-full p-2.5 rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 text-indigo-700 text-xs font-bold transition flex items-center justify-center gap-2 hover:bg-indigo-100"
          >
            <Zap className="w-3.5 h-3.5 text-indigo-600 fill-indigo-600" />
            <span>Click to Fill Pre-Seeded Demo Credentials</span>
          </button>

          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-2.5 text-xs text-rose-700 animate-slideUp">
              <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
              <span>{error}</span>
            </div>
          )}

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

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-bold text-slate-700">Password</label>
                <button
                  type="button"
                  onClick={onNavigateForgot}
                  className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-700"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-10 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none transition"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 text-white text-xs sm:text-sm font-bold shadow-md shadow-indigo-200 transition flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
              <span>{loading ? 'Authenticating...' : 'Sign In to Workspace'}</span>
            </button>
          </form>

          <div className="pt-4 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-500">
              Don't have an account yet?{' '}
              <button
                type="button"
                onClick={onNavigateRegister}
                className="font-bold text-indigo-600 hover:text-indigo-700 hover:underline"
              >
                Create student account
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
