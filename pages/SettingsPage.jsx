import React, { useState, useEffect } from 'react';
import { Settings, ShieldCheck, Key, Cpu, CheckCircle2, AlertCircle, Loader2, Database, Sparkles } from 'lucide-react';
import { api } from '../api';
import { useToast } from '../context/ToastContext';

export default function SettingsPage() {
  const [settingsData, setSettingsData] = useState(null);
  const [claudeKey, setClaudeKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  useEffect(() => {
    async function fetchSettings() {
      try {
        const data = await api.getSettings();
        setSettingsData(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchSettings();
  }, []);

  const handleSaveKeys = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.updateSettings({
        provider: 'auto',
        claude_api_key: claudeKey || undefined,
        openai_api_key: openaiKey || undefined,
        gemini_api_key: geminiKey || undefined
      });
      toast.success('AI API Keys updated for this session!');
      const updated = await api.getSettings();
      setSettingsData(updated);
    } catch (err) {
      toast.error(err.message || 'Failed to update settings.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-xs space-y-6">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            <Settings className="w-5 h-5 text-indigo-600" />
            <span>AI Platform Configuration & Guardrails</span>
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Manage LLM model providers, ChromaDB vector store parameters, and strict citation enforcement.
          </p>
        </div>

        {/* Current Active Engine Status Card */}
        <div className="p-5 rounded-2xl bg-indigo-50/70 border border-indigo-100/90 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-indigo-900 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-indigo-600" />
              Active RAG Engine Status
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold border border-emerald-200">
              Operational
            </span>
          </div>

          <p className="text-sm font-extrabold text-indigo-950">
            {settingsData?.active_provider || 'Built-in Grounded Academic RAG Engine'}
          </p>

          <div className="pt-2 border-t border-indigo-100 text-[11px] text-indigo-700 flex flex-wrap gap-x-4 gap-y-1.5 font-medium">
            <span className="flex items-center gap-1">
              <Database className="w-3.5 h-3.5" />
              Vector Database: <strong>ChromaDB</strong>
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              Guardrails: <strong>Strict Provenance (0% Hallucination)</strong>
            </span>
          </div>
        </div>

        {/* Optional Custom API Key Form */}
        <form onSubmit={handleSaveKeys} className="space-y-4 pt-2">
          <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
            <Key className="w-4 h-4 text-slate-400" />
            <span>External LLM API Keys (Optional)</span>
          </h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            StudyMate AI runs out of the box with its built-in offline engine. To elevate answers using Anthropic Claude 3 or OpenAI GPT-4o, enter your API key below:
          </p>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Anthropic Claude API Key
              </label>
              <input
                type="password"
                value={claudeKey}
                onChange={(e) => setClaudeKey(e.target.value)}
                placeholder="sk-ant-api..."
                className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                OpenAI API Key
              </label>
              <input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-proj-..."
                className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Google Gemini API Key
              </label>
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none font-mono"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={saving || (!claudeKey && !openaiKey && !geminiKey)}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-40 text-white text-xs font-bold shadow-md transition flex items-center gap-1.5"
          >
            {saving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>Save API Configuration</span>
          </button>
        </form>

        {/* Database Architecture Info */}
        <div className="pt-6 border-t border-slate-100 text-xs text-slate-500 space-y-2">
          <h4 className="font-bold text-slate-700">Relational & Vector Storage Architecture</h4>
          <p className="leading-relaxed">
            User accounts, documents, chat history, quiz attempts, and flashcards are persisted via SQLAlchemy (PostgreSQL / SQLite). Vector embeddings are handled by ChromaDB using dense cosine similarity retrieval.
          </p>
        </div>
      </div>
    </div>
  );
}
