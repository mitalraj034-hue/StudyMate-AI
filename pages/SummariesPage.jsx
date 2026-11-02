import React, { useState, useEffect } from 'react';
import {
  FileText,
  Sparkles,
  BookOpen,
  Copy,
  Check,
  RefreshCw,
  Layers,
  Award,
  ListOrdered,
  Code,
  Tag,
  Bookmark,
  ChevronRight,
  ChevronDown,
  Download,
  Sliders,
  Scissors,
  HelpCircle,
  Lightbulb,
  ExternalLink
} from 'lucide-react';
import { api } from '../api';
import { useToast } from '../context/ToastContext';

// Helper to render formatted markdown cleanly without raw symbols
function CleanMarkdownRenderer({ text }) {
  if (!text) return null;

  const lines = text.split('\n');
  const renderedElements = [];
  let tableRows = [];
  let inTable = false;
  let codeBlock = [];
  let inCode = false;

  const renderInline = (str) => {
    // Bold: **text**
    const parts = str.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-extrabold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      // Inline code: `code`
      const codeParts = part.split(/(`[^`]+`)/g);
      return codeParts.map((cp, j) => {
        if (cp.startsWith('`') && cp.endsWith('`')) {
          return (
            <code key={j} className="px-1.5 py-0.5 rounded bg-slate-100 font-mono text-xs text-indigo-700">
              {cp.slice(1, -1)}
            </code>
          );
        }
        return cp;
      });
    });
  };

  lines.forEach((line, idx) => {
    const trimmed = line.trim();

    // Code blocks
    if (trimmed.startsWith('```')) {
      if (inCode) {
        renderedElements.push(
          <div key={`code-${idx}`} className="p-3.5 my-2.5 rounded-xl bg-slate-900 font-mono text-xs text-emerald-300 overflow-x-auto border border-slate-800">
            <pre>{codeBlock.join('\n')}</pre>
          </div>
        );
        codeBlock = [];
        inCode = false;
      } else {
        inCode = true;
      }
      return;
    }
    if (inCode) {
      codeBlock.push(line);
      return;
    }

    // Markdown Tables
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      if (!inTable) inTable = true;
      // Skip markdown separator line
      if (!trimmed.includes('---')) {
        const cells = trimmed.split('|').filter((c, i, arr) => i > 0 && i < arr.length - 1).map(c => c.trim());
        tableRows.push(cells);
      }
      return;
    } else if (inTable) {
      if (tableRows.length > 0) {
        renderedElements.push(
          <div key={`table-${idx}`} className="my-3 overflow-x-auto rounded-xl border border-slate-200">
            <table className="min-w-full text-xs text-slate-700 divide-y divide-slate-200">
              <thead className="bg-slate-50 font-bold text-slate-800">
                <tr>
                  {tableRows[0]?.map((head, hIdx) => (
                    <th key={hIdx} className="px-3.5 py-2 text-left">{head}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {tableRows.slice(1).map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-slate-50/60">
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-3.5 py-2">{renderInline(cell)}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      tableRows = [];
      inTable = false;
    }

    if (!trimmed) {
      renderedElements.push(<div key={`sp-${idx}`} className="h-2" />);
      return;
    }

    // H1 Heading
    if (trimmed.startsWith('# ')) {
      renderedElements.push(
        <h2 key={idx} className="text-base sm:text-lg font-black text-slate-900 mt-4 mb-2 pb-1.5 border-b border-slate-100">
          {trimmed.slice(2)}
        </h2>
      );
      return;
    }

    // H2 Heading
    if (trimmed.startsWith('## ')) {
      renderedElements.push(
        <h3 key={idx} className="text-sm sm:text-base font-extrabold text-indigo-950 mt-3.5 mb-1.5">
          {trimmed.slice(3)}
        </h3>
      );
      return;
    }

    // H3 Heading
    if (trimmed.startsWith('### ')) {
      renderedElements.push(
        <h4 key={idx} className="text-xs sm:text-sm font-bold text-indigo-900 mt-3 mb-1">
          {trimmed.slice(4)}
        </h4>
      );
      return;
    }

    // Bullet points
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ') || trimmed.startsWith('• ')) {
      const content = trimmed.replace(/^[-*•]\s+/, '');
      renderedElements.push(
        <div key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-slate-700 my-1 pl-1">
          <span className="text-indigo-600 font-bold mt-1 text-xs">•</span>
          <div className="leading-relaxed">{renderInline(content)}</div>
        </div>
      );
      return;
    }

    // Numbered list: 1. , 2.
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      renderedElements.push(
        <div key={idx} className="flex items-start gap-2 text-xs sm:text-sm text-slate-700 my-1 pl-1">
          <span className="font-bold text-indigo-600 min-w-[18px] text-xs mt-0.5">{numMatch[1]}.</span>
          <div className="leading-relaxed">{renderInline(numMatch[2])}</div>
        </div>
      );
      return;
    }

    // Standard paragraph
    renderedElements.push(
      <p key={idx} className="text-xs sm:text-sm text-slate-700 leading-relaxed font-normal my-1">
        {renderInline(trimmed)}
      </p>
    );
  });

  return <div className="space-y-1">{renderedElements}</div>;
}

export default function SummariesPage({ activeDocId, documents = [] }) {
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  // Advanced Summary Controls
  const [summaryType, setSummaryType] = useState('Detailed Summary');
  const [summaryLength, setSummaryLength] = useState('Detailed');
  const [topicFocus, setTopicFocus] = useState('');
  const [expandedChapter, setExpandedChapter] = useState(0);

  const toast = useToast();
  const selectedDoc = documents.find((d) => d.id === Number(activeDocId));

  const loadSummary = async (overrideParams = {}) => {
    if (!activeDocId) return;
    setLoading(true);
    try {
      const targetType = overrideParams.summaryType || summaryType;
      const targetLength = overrideParams.length || summaryLength;
      const targetTopic = overrideParams.topic !== undefined ? overrideParams.topic : topicFocus;

      const data = await api.generateSummary(activeDocId, {
        summaryType: targetType,
        length: targetLength,
        topic: targetTopic ? targetTopic.trim() : null
      });

      setSummaryData(data);
    } catch (err) {
      console.error('Failed to load summary:', err);
      toast.error('Failed to generate summary: ' + (err.message || 'Server error'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, [activeDocId]);

  const handleApplyConfig = () => {
    loadSummary();
  };

  const handleCopy = () => {
    if (!summaryData) return;
    const docTitle = selectedDoc?.original_filename || selectedDoc?.original_name || 'Document';
    const textToCopy = summaryData.markdown_summary || summaryData.detailed_summary || summaryData.executive_summary || '';
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    toast.success('Summary copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!summaryData) return;
    const text = summaryData.markdown_summary || summaryData.detailed_summary || '';
    const blob = new Blob([text], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${summaryData.title || 'StudyMate_Summary'}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Markdown file downloaded!');
  };

  // Action helpers
  const handleAction = async (actionType) => {
    if (!activeDocId || loading) return;

    if (actionType === 'more_detailed') {
      setSummaryLength('Very Detailed');
      toast.info('Generating exhaustive, very detailed study breakdown...');
      await loadSummary({ length: 'Very Detailed' });
    } else if (actionType === 'simplify') {
      toast.info('Synthesizing beginner-friendly summary...');
      await loadSummary({ summaryType: 'Quick Summary', length: 'Short' });
    } else if (actionType === 'exam_notes') {
      setSummaryType('Exam Notes');
      toast.info('Generating high-yield exam preparation notes...');
      await loadSummary({ summaryType: 'Exam Notes' });
    } else if (actionType === 'quiz') {
      toast.info('Generating practice quiz from this document summary...');
      try {
        await api.generateQuiz(activeDocId, 5, 'Medium', null, summaryData?.title || 'Summary Review');
        toast.success('Quiz generated! Switch to Quiz tab to practice.');
      } catch (e) {
        toast.error('Failed to generate quiz: ' + e.message);
      }
    } else if (actionType === 'flashcards') {
      toast.info('Generating flashcards from this document summary...');
      try {
        await api.generateFlashcards(activeDocId, 8, summaryData?.title || null);
        toast.success('Flashcards created! Switch to Flashcards tab to study.');
      } catch (e) {
        toast.error('Failed to generate flashcards: ' + e.message);
      }
    }
  };

  if (!selectedDoc) {
    return (
      <div className="p-12 text-center bg-white rounded-3xl border border-slate-200/80 shadow-sm max-w-xl mx-auto mt-10">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-800">No Document Selected</h3>
        <p className="text-xs text-slate-500 mt-1">Please select or upload a document to generate its smart academic summary.</p>
      </div>
    );
  }

  const docName = selectedDoc.original_filename || selectedDoc.original_name || selectedDoc.filename;
  const chapters = summaryData?.chapter_breakdown || summaryData?.chapter_summary || [];
  const examNotes = summaryData?.exam_notes || [];
  const definitions = summaryData?.key_definitions || [];
  const formulas = summaryData?.formulas_and_algorithms || summaryData?.formulas || [];
  const topics = summaryData?.important_topics || summaryData?.key_concepts || [];

  return (
    <div className="space-y-5 max-w-5xl mx-auto animate-fadeIn">
      {/* Top Header Bar */}
      <div className="bg-white p-5 sm:p-6 rounded-3xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 text-[10px] font-bold uppercase tracking-wider">
              Smart Academic Synthesis
            </span>
            <span className="text-xs text-slate-400">
              {summaryData?.total_pages_analyzed || selectedDoc.page_count || selectedDoc.pages || 0} Pages Analyzed
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
            {docName}
          </h2>
        </div>

        {/* Right Action buttons */}
        <div className="flex flex-wrap items-center gap-2 self-stretch md:self-auto">
          <button
            onClick={() => loadSummary()}
            disabled={loading}
            className="px-3 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-bold transition flex items-center gap-1.5"
            title="Regenerate"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>

          <button
            onClick={handleCopy}
            disabled={!summaryData || loading}
            className="px-3 py-2 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-bold transition flex items-center gap-1.5"
            title="Copy Content"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleDownload}
            disabled={!summaryData || loading}
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 text-white text-xs font-bold shadow-sm transition flex items-center gap-1.5"
            title="Download Markdown"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export .md</span>
          </button>
        </div>
      </div>

      {/* Control Panel: Summary Type, Length, Topic */}
      <div className="bg-white p-4 sm:p-5 rounded-3xl border border-slate-200/80 shadow-xs space-y-3">
        {/* Summary Types Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1 shrink-0">Type:</span>
          {[
            'Quick Summary',
            'Detailed Summary',
            'Chapter-wise Summary',
            'Exam Notes',
            'Last-Minute Revision',
            'Topic-wise Summary'
          ].map((type) => (
            <button
              key={type}
              onClick={() => {
                setSummaryType(type);
                loadSummary({ summaryType: type });
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold shrink-0 transition ${
                summaryType === type
                  ? 'bg-purple-600 text-white shadow-xs'
                  : 'bg-slate-50 border border-slate-200/80 text-slate-700 hover:bg-slate-100'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {/* Secondary options row: Length & Topic input */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-slate-100">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">Length Depth:</span>
            <div className="flex items-center gap-1">
              {['Short', 'Medium', 'Detailed', 'Very Detailed'].map((len) => (
                <button
                  key={len}
                  onClick={() => {
                    setSummaryLength(len);
                    loadSummary({ length: len });
                  }}
                  className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition ${
                    summaryLength === len
                      ? 'bg-slate-800 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {len}
                </button>
              ))}
            </div>
          </div>

          {/* Topic Filter for Topic-wise summary */}
          {summaryType === 'Topic-wise Summary' && (
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <input
                type="text"
                value={topicFocus}
                onChange={(e) => setTopicFocus(e.target.value)}
                placeholder="Enter topic (e.g. Chapter 2, Neural Networks)..."
                className="px-3 py-1 text-xs rounded-xl border border-slate-200 bg-slate-50 text-slate-800 outline-none w-full sm:w-60 focus:border-purple-500"
              />
              <button
                onClick={handleApplyConfig}
                className="px-3 py-1 bg-purple-600 text-white text-xs font-bold rounded-xl shadow-xs shrink-0"
              >
                Summarize Topic
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      {loading ? (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200/80 shadow-xs space-y-3">
          <Sparkles className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
          <h4 className="text-sm font-bold text-slate-800">Synthesizing {summaryType}...</h4>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Google Gemini is analyzing the complete PDF text, chapters, formulas, and definitions to generate your academic study document.
          </p>
        </div>
      ) : summaryData ? (
        <div className="space-y-6">
          {/* Executive Overview Highlight */}
          {summaryData.executive_summary && (
            <div className="p-5 sm:p-6 rounded-3xl bg-purple-50/50 border border-purple-100 space-y-2.5">
              <div className="flex items-center gap-2 text-purple-900 font-extrabold text-xs uppercase tracking-wider">
                <Lightbulb className="w-4 h-4 text-purple-600" />
                <span>Executive Overview</span>
              </div>
              <p className="text-xs sm:text-sm text-purple-950 leading-relaxed font-medium">
                {summaryData.executive_summary}
              </p>
            </div>
          )}

          {/* Full Clean Markdown Viewer */}
          {summaryData.detailed_summary && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <h3 className="font-bold text-sm sm:text-base text-slate-900">
                  {summaryData.title || `${summaryType} Analysis`}
                </h3>
                <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600">
                  {summaryLength}
                </span>
              </div>
              <CleanMarkdownRenderer text={summaryData.detailed_summary} />
            </div>
          )}

          {/* Chapter-wise Accordion Breakdown (for Chapter-wise Summary) */}
          {chapters.length > 0 && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-indigo-700 font-bold text-xs uppercase tracking-wider">
                <BookOpen className="w-4 h-4" />
                <span>Chapter Breakdown ({chapters.length} Sections)</span>
              </div>

              <div className="space-y-3">
                {chapters.map((ch, idx) => {
                  const isExpanded = expandedChapter === idx;
                  return (
                    <div
                      key={idx}
                      className="rounded-2xl border border-slate-200 overflow-hidden transition"
                    >
                      <button
                        onClick={() => setExpandedChapter(isExpanded ? -1 : idx)}
                        className="w-full p-4 bg-slate-50/80 hover:bg-slate-100/80 flex items-center justify-between text-left transition"
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-lg bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center shrink-0">
                            {idx + 1}
                          </span>
                          <div>
                            <h4 className="text-xs sm:text-sm font-bold text-slate-900">
                              {ch.title || ch.chapter_title || `Chapter ${idx + 1}`}
                            </h4>
                            {ch.pages && (
                              <span className="text-[10px] text-slate-400 font-medium">
                                {ch.pages}
                              </span>
                            )}
                          </div>
                        </div>
                        {isExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                      </button>

                      {isExpanded && (
                        <div className="p-4 sm:p-5 bg-white border-t border-slate-100 space-y-3 text-xs sm:text-sm text-slate-700 leading-relaxed">
                          <p>{ch.summary}</p>
                          {(ch.key_takeaways || ch.key_points) && (
                            <div className="space-y-1.5 pt-2">
                              <span className="font-bold text-[11px] text-slate-500 uppercase tracking-wider block">
                                Core Takeaways:
                              </span>
                              {(ch.key_takeaways || ch.key_points).map((pt, pIdx) => (
                                <div key={pIdx} className="flex items-start gap-2 text-xs text-slate-600">
                                  <span className="text-indigo-600 font-bold">•</span>
                                  <span>{pt}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Exam Notes Section (if available) */}
          {examNotes.length > 0 && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-amber-700 font-bold text-xs uppercase tracking-wider">
                <Award className="w-4 h-4" />
                <span>Frequently Examinable Concepts & Notes</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {examNotes.map((note, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-2xl bg-amber-50/40 border border-amber-200/60 text-xs text-slate-800 flex items-start gap-2.5 font-medium leading-relaxed"
                  >
                    <div className="w-2 h-2 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <span>{note}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Definitions Glossary */}
          {definitions.length > 0 && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-4">
              <div className="flex items-center gap-2 text-teal-700 font-bold text-xs uppercase tracking-wider">
                <Bookmark className="w-4 h-4" />
                <span>Key Definitions & Technical Terminology</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {definitions.map((def, idx) => (
                  <div key={idx} className="p-3.5 rounded-2xl bg-teal-50/30 border border-teal-100/80 space-y-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-teal-900">{def.term}</h4>
                      {def.page && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-teal-100/70 text-teal-800">
                          Page {def.page}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-700 leading-relaxed">{def.definition}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Action Footer Bar */}
          <div className="p-4 sm:p-5 rounded-3xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs font-bold text-slate-600">Explore further with this document:</span>
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => handleAction('more_detailed')}
                className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-bold transition"
              >
                Make It More Detailed
              </button>
              <button
                onClick={() => handleAction('simplify')}
                className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-bold transition"
              >
                Simplify Language
              </button>
              <button
                onClick={() => handleAction('exam_notes')}
                className="px-3 py-1.5 rounded-xl bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-bold transition"
              >
                Create Exam Notes
              </button>
              <button
                onClick={() => handleAction('quiz')}
                className="px-3 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition"
              >
                Generate Quiz
              </button>
              <button
                onClick={() => handleAction('flashcards')}
                className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition"
              >
                Create Flashcards
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
