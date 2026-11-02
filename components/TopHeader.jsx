import React from 'react';
import { Menu, Plus, FileText, ShieldCheck, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function TopHeader({
  title,
  subtitle,
  documents = [],
  activeDocId,
  setActiveDocId,
  onOpenUpload,
  setIsMobileOpen
}) {
  const { user } = useAuth();
  const selectedDoc = documents.find((d) => d.id === Number(activeDocId));

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-4 sm:px-8 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Title & Mobile Menu Button */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={() => setIsMobileOpen(true)}
          className="p-2 rounded-xl text-slate-500 hover:bg-slate-100 lg:hidden shrink-0"
          title="Open Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="min-w-0">
          <h1 className="text-base sm:text-lg font-extrabold text-slate-900 leading-tight truncate">
            {title}
          </h1>
          {subtitle && (
            <p className="text-xs text-slate-400 hidden sm:block truncate">{subtitle}</p>
          )}
        </div>
      </div>

      {/* Action Controls & Document Selector */}
      <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
        {/* Active Document Selector */}
        {documents.length > 0 && (
          <div className="relative flex items-center">
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200/90 rounded-xl px-3 py-1.5 text-xs text-slate-700 shadow-xs">
              <FileText className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
              <select
                value={activeDocId || ''}
                onChange={(e) => setActiveDocId(Number(e.target.value))}
                className="bg-transparent text-xs font-semibold text-slate-800 outline-none cursor-pointer max-w-[130px] sm:max-w-[210px] truncate"
              >
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.original_filename || doc.original_name || doc.filename}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Grounding Guardrail Pill */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Strict Citation Grounded</span>
        </div>

        {/* Upload Button */}
        <button
          onClick={onOpenUpload}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white text-xs font-bold shadow-sm hover:shadow transition transform hover:-translate-y-0.5"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Upload PDF</span>
        </button>
      </div>
    </header>
  );
}
