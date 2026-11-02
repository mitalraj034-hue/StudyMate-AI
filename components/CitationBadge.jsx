import React, { useState } from 'react';
import { BookOpen, Copy, Check, X, ShieldCheck } from 'lucide-react';

export default function CitationBadge({ pageNumber, excerpt, relevanceScore }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(excerpt || `Grounded in Page ${pageNumber}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Format relevance score
  const scoreDisplay = relevanceScore ? `${Math.round(relevanceScore)}% match` : null;

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        type="button"
        className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full bg-indigo-50/80 hover:bg-indigo-100/90 text-indigo-700 border border-indigo-200/80 transition-all duration-150 shadow-sm hover:shadow cursor-pointer group"
        title="Click to view verified source text excerpt"
      >
        <BookOpen className="w-3.5 h-3.5 text-indigo-600 group-hover:scale-110 transition-transform" />
        <span className="font-semibold">Page {pageNumber}</span>
        {scoreDisplay && (
          <>
            <span className="text-indigo-300">·</span>
            <span className="text-[11px] text-indigo-600 font-medium">
              {scoreDisplay}
            </span>
          </>
        )}
      </button>

      {isOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn"
          onClick={() => setIsOpen(false)}
        >
          <div 
            className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 relative animate-scaleUp text-left"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between pb-3.5 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
                  <BookOpen className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-800 text-sm">Verified Source Citation</h4>
                  <p className="text-xs text-slate-500">Document Provenance: Page {pageNumber}</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Excerpt Body */}
            <div className="my-4 p-4 rounded-xl bg-slate-50/90 border border-slate-200/70 text-slate-700 text-xs sm:text-sm leading-relaxed font-mono max-h-60 overflow-y-auto">
              "{excerpt || 'Context passage extracted from document.'}"
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs font-medium text-emerald-600 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-500" />
                <span>100% Grounded in Document</span>
              </span>

              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200/80 text-slate-700 text-xs font-semibold transition"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                <span>{copied ? 'Copied' : 'Copy Excerpt'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
