import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Bot,
  User,
  Sparkles,
  BookOpen,
  Copy,
  Check,
  ShieldCheck,
  AlertCircle,
  FileText,
  Loader2,
  Trash2,
  HelpCircle,
  ChevronDown,
  CheckCircle,
  Info,
  Lightbulb,
  FileSpreadsheet,
  CornerDownRight,
  GraduationCap,
  Languages,
  RotateCw,
  Scissors,
  HelpCircle as QuestionIcon,
  Layers,
  ArrowRight
} from 'lucide-react';
import { api } from '../api';
import CitationBadge from '../components/CitationBadge';
import { useToast } from '../context/ToastContext';

// Helper to parse inline markdown (bold, italic, code)
function parseInlineMarkdown(text) {
  if (!text) return null;
  const tokens = [];
  const inlineRegex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = inlineRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      tokens.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('`') && token.endsWith('`')) {
      tokens.push(
        <code key={`code-${key++}`} className="px-1.5 py-0.5 rounded bg-slate-100 text-indigo-700 font-mono text-[11px] sm:text-[12px] border border-slate-200">
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('**') && token.endsWith('**')) {
      tokens.push(
        <strong key={`bold-${key++}`} className="font-semibold text-slate-900">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      tokens.push(
        <em key={`em-${key++}`} className="italic text-slate-700">
          {token.slice(1, -1)}
        </em>
      );
    }
    lastIndex = inlineRegex.lastIndex;
  }
  if (lastIndex < text.length) {
    tokens.push(text.substring(lastIndex));
  }
  return tokens.length > 0 ? tokens : text;
}

// Clean, flowing natural conversational markdown renderer (like ChatGPT)
function FormattedAssistantMessage({ content }) {
  if (!content) return null;

  const lines = content.split('\n');
  const elements = [];
  let inCodeBlock = false;
  let codeBuffer = [];
  let listBuffer = [];
  let listType = null; // 'ul' or 'ol'
  let elementKey = 0;

  const flushList = () => {
    if (listBuffer.length > 0) {
      if (listType === 'ol') {
        elements.push(
          <ol key={`ol-${elementKey++}`} className="space-y-1.5 my-2 pl-5 list-decimal text-slate-800 text-xs sm:text-sm">
            {listBuffer.map((item, i) => (
              <li key={i} className="pl-1">
                {parseInlineMarkdown(item)}
              </li>
            ))}
          </ol>
        );
      } else {
        elements.push(
          <ul key={`ul-${elementKey++}`} className="space-y-1.5 my-2 pl-2 text-slate-800 text-xs sm:text-sm">
            {listBuffer.map((item, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 shrink-0" />
                <span className="flex-1">{parseInlineMarkdown(item)}</span>
              </li>
            ))}
          </ul>
        );
      }
      listBuffer = [];
      listType = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code block toggle (```...```)
    if (line.trim().startsWith('```')) {
      flushList();
      if (inCodeBlock) {
        elements.push(
          <div key={`code-block-${elementKey++}`} className="my-2.5 rounded-xl bg-slate-900 text-slate-100 p-3 sm:p-4 font-mono text-xs overflow-x-auto border border-slate-800 shadow-xs">
            <pre className="whitespace-pre">{codeBuffer.join('\n')}</pre>
          </div>
        );
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    // Unordered list item (- or *)
    const ulMatch = line.match(/^[\*\-]\s+(.*)$/);
    if (ulMatch) {
      if (listType === 'ol') flushList();
      listType = 'ul';
      listBuffer.push(ulMatch[1]);
      continue;
    }

    // Ordered list item (1. 2. etc)
    const olMatch = line.match(/^\d+[\.\)]\s+(.*)$/);
    if (olMatch) {
      if (listType === 'ul') flushList();
      listType = 'ol';
      listBuffer.push(olMatch[1]);
      continue;
    }

    // Flush any open list before handling non-list lines
    flushList();

    // Empty blank line
    if (!line.trim()) {
      elements.push(<div key={`empty-${elementKey++}`} className="h-1.5" />);
      continue;
    }

    // Blockquote (> text)
    if (line.startsWith('>')) {
      elements.push(
        <div key={`quote-${elementKey++}`} className="border-l-3 border-indigo-500 bg-indigo-50/40 pl-3 py-1 my-1.5 rounded-r-lg text-slate-700 italic text-xs sm:text-sm">
          {parseInlineMarkdown(line.replace(/^>\s*/, ''))}
        </div>
      );
      continue;
    }

    // Markdown Headings
    if (line.startsWith('### ')) {
      elements.push(
        <h4 key={`h3-${elementKey++}`} className="text-xs sm:text-sm font-bold text-slate-900 mt-3 mb-1 flex items-center gap-1.5">
          <span className="w-1.5 h-3.5 bg-indigo-600 rounded-full inline-block" />
          <span>{parseInlineMarkdown(line.slice(4))}</span>
        </h4>
      );
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h3 key={`h2-${elementKey++}`} className="text-sm sm:text-base font-bold text-slate-900 mt-3.5 mb-1.5">
          {parseInlineMarkdown(line.slice(3))}
        </h3>
      );
      continue;
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h2 key={`h1-${elementKey++}`} className="text-base sm:text-lg font-bold text-slate-900 mt-4 mb-2">
          {parseInlineMarkdown(line.slice(2))}
        </h2>
      );
      continue;
    }

    // Standard conversational paragraph
    elements.push(
      <p key={`p-${elementKey++}`} className="text-xs sm:text-sm text-slate-800 leading-relaxed font-normal">
        {parseInlineMarkdown(line)}
      </p>
    );
  }

  flushList();

  return <div className="space-y-2">{elements}</div>;
}

export default function ChatPage({ activeDocId, documents = [], setActiveDocId }) {
  const [messages, setMessages] = useState([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  
  // Personal Tutor Controls
  const [explanationMode, setExplanationMode] = useState('Detailed Explanation');
  const [learningLevel, setLearningLevel] = useState('Intermediate');
  const [language, setLanguage] = useState('English');

  const messagesEndRef = useRef(null);
  const toast = useToast();

  const selectedDoc = documents.find((d) => d.id === Number(activeDocId));

  const fetchHistory = async () => {
    if (!activeDocId) return;
    try {
      const history = await api.getChatHistory(activeDocId);
      const formatted = history.map((item) => {
        if (item.question && item.answer) {
          return [
            {
              id: `q-${item.id}`,
              role: 'user',
              content: item.question,
              created_at: item.created_at
            },
            {
              id: `a-${item.id}`,
              role: 'assistant',
              content: item.answer,
              citations: item.citations || [],
              created_at: item.created_at,
              follow_up_suggestions: [
                "Explain in Hinglish 🇮🇳",
                "Give another practical example 💡",
                "Teach this step-by-step 🪜",
                "Test my understanding 📝"
              ]
            }
          ];
        }
        return item;
      }).flat();
      setMessages(formatted);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [activeDocId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText = inputQuery, actionOverride = null) => {
    const text = (typeof queryText === 'string' ? queryText : inputQuery).trim();
    if (!text || !activeDocId || loading) return;

    // Display appropriate user message in conversation
    const userLabel = actionOverride ? (
      actionOverride === 'explain_more' ? 'Explain more details' :
      actionOverride === 'give_example' ? 'Give another example' :
      actionOverride === 'make_shorter' ? 'Make it shorter and concise' :
      actionOverride === 'in_hinglish' ? 'Explain in Hinglish' :
      actionOverride === 'in_hindi' ? 'Explain in Hindi' :
      text
    ) : text;

    const tempUserMsg = {
      id: Date.now(),
      role: 'user',
      content: userLabel,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    if (!actionOverride) {
      setInputQuery('');
    }

    setLoading(true);

    try {
      const res = await api.chatWithDocument(activeDocId, text, {
        mode: explanationMode,
        level: learningLevel,
        language: language,
        action: actionOverride
      });

      const botMsg = {
        id: res.chat_history_id || res.message_id || Date.now() + 1,
        role: 'assistant',
        content: res.answer,
        citations: res.citations || [],
        confidence: res.confidence,
        grounded: res.grounded,
        follow_up_suggestions: res.follow_up_suggestions || [
          "Explain in Hinglish 🇮🇳",
          "Give an example 💡",
          "Make it shorter ✂️",
          "Ask me a question 📝"
        ],
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to retrieve answer. Please try again.'}`,
        citations: [],
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
      toast.error(err.message || 'Inquiry failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (actionType, lastUserMsgText = null) => {
    if (!activeDocId || loading) return;

    // Find the latest user query
    let queryToUse = lastUserMsgText;
    if (!queryToUse) {
      const reversed = [...messages].reverse();
      const lastUser = reversed.find((m) => m.role === 'user');
      queryToUse = lastUser ? lastUser.content : "the concepts in this document";
    }

    if (actionType === 'in_hindi') {
      setLanguage('Hindi');
      toast.info('Switching tutor language to Hindi (हिन्दी)...');
      await handleSend(queryToUse, 'in_hindi');
    } else if (actionType === 'in_hinglish') {
      setLanguage('Hinglish');
      toast.info('Switching tutor language to Hinglish...');
      await handleSend(queryToUse, 'in_hinglish');
    } else if (actionType === 'explain_more') {
      toast.info('Requesting in-depth breakdown...');
      await handleSend(`Explain more details about: ${queryToUse}`, 'explain_more');
    } else if (actionType === 'give_example') {
      toast.info('Generating relatable example...');
      await handleSend(`Give me another real-life example for: ${queryToUse}`, 'give_example');
    } else if (actionType === 'make_shorter') {
      toast.info('Generating concise summary...');
      await handleSend(`Make this explanation shorter and concise: ${queryToUse}`, 'make_shorter');
    } else if (actionType === 'step_by_step') {
      toast.info('Explaining step-by-step...');
      await handleSend(`Can you break down step-by-step: ${queryToUse}`);
    } else if (actionType === 'ask_question') {
      toast.info('Generating practice question...');
      await handleSend(`Ask me a question to test my understanding of this.`);
    } else if (actionType === 'generate_quiz') {
      toast.info('Generating dynamic quiz on this topic...');
      try {
        await api.generateQuiz(activeDocId, 5, 'Medium', null, queryToUse);
        toast.success('Quiz generated! Open Quiz tab to practice.');
      } catch (e) {
        toast.error('Failed to generate quiz: ' + e.message);
      }
    } else if (actionType === 'create_flashcards') {
      toast.info('Generating flashcards on this topic...');
      try {
        await api.generateFlashcards(activeDocId, 8, queryToUse);
        toast.success('Flashcards created! Open Flashcards tab to study.');
      } catch (e) {
        toast.error('Failed to generate flashcards: ' + e.message);
      }
    }
  };

  const handleClearChat = async () => {
    if (!activeDocId || messages.length === 0) return;
    if (!window.confirm('Are you sure you want to clear the conversation history for this document?')) {
      return;
    }

    setClearing(true);
    try {
      await api.clearChatHistory(activeDocId);
      setMessages([]);
      toast.success('Chat history cleared successfully.');
    } catch (err) {
      console.error('Failed to clear chat:', err);
      toast.error('Failed to clear chat history.');
    } finally {
      setClearing(false);
    }
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Response copied to clipboard!');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const quickPrompts = [
    'I don’t understand Chapter 3. Explain it to me in a simple way.',
    'What are the foundational principles described in this document?',
    'Explain the most difficult concept here step by step with an analogy.',
    'What are the most probable exam questions and key definitions?'
  ];

  if (!selectedDoc) {
    return (
      <div className="p-12 text-center bg-white rounded-3xl border border-slate-200/80 shadow-sm max-w-xl mx-auto mt-10">
        <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-800">No Document Selected</h3>
        <p className="text-xs text-slate-500 mt-1">Please select or upload a document to begin learning with your AI Personal Tutor.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden animate-fadeIn">
      {/* Top Banner with Doc Info and Clear Chat */}
      <div className="px-5 py-3 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600 shrink-0">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div className="overflow-hidden">
            <div className="flex items-center gap-2">
              <h3 className="text-xs sm:text-sm font-bold text-slate-900 truncate">
                {selectedDoc.original_filename || selectedDoc.original_name || selectedDoc.filename}
              </h3>
              <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold border border-emerald-200">
                AI Tutor Active
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              {selectedDoc.page_count || selectedDoc.pages || 0} Pages • Chapter-Aware RAG Semantic Search
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              disabled={clearing}
              title="Clear conversation history"
              className="p-1.5 sm:px-2.5 sm:py-1 rounded-xl bg-slate-100 hover:bg-rose-50 text-slate-500 hover:text-rose-600 text-xs font-semibold transition border border-slate-200/60 flex items-center gap-1.5"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{clearing ? 'Clearing...' : 'Clear Chat'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Tutor Mode & Controls Bar */}
      <div className="px-5 py-2.5 bg-white border-b border-slate-100 flex flex-wrap items-center justify-between gap-2.5 text-xs">
        {/* Mode Selector */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none py-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mr-1 shrink-0">Mode:</span>
          {[
            'Simple Explanation',
            'Step-by-Step Teaching',
            'Detailed Explanation',
            'Exam Preparation',
            'Quick Revision',
            'Real-Life Examples'
          ].map((mode) => (
            <button
              key={mode}
              onClick={() => setExplanationMode(mode)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-bold shrink-0 transition ${
                explanationMode === mode
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>

        {/* Level and Language selectors */}
        <div className="flex items-center gap-2 shrink-0">
          <select
            value={learningLevel}
            onChange={(e) => setLearningLevel(e.target.value)}
            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-50 border border-slate-200 text-slate-700 outline-none cursor-pointer"
            title="Student Learning Level"
          >
            <option value="Beginner">Beginner Level</option>
            <option value="Intermediate">Intermediate Level</option>
            <option value="Advanced">Advanced Level</option>
          </select>

          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-50 border border-slate-200 text-slate-700 outline-none cursor-pointer"
            title="Tutor Language"
          >
            <option value="English">English</option>
            <option value="Hinglish">Hinglish</option>
            <option value="Hindi">Hindi (हिन्दी)</option>
          </select>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-5">
        {messages.length === 0 ? (
          <div className="py-8 text-center max-w-md mx-auto space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto shadow-xs">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-base font-bold text-slate-900">Your AI Personal Tutor is Ready</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Ask about any chapter, request simple analogies, exam tips, or step-by-step teaching. Gemini will explain concepts patiently and check your understanding.
              </p>
            </div>

            {/* Quick Prompt Suggestions */}
            <div className="pt-2 space-y-2 text-left">
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider text-center">
                Suggested Tutor Inquiries
              </p>
              {quickPrompts.map((p, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(p)}
                  className="w-full text-left p-3 rounded-xl bg-slate-50 hover:bg-indigo-50/70 border border-slate-200/80 hover:border-indigo-200 text-xs text-slate-700 font-medium transition flex items-center justify-between group"
                >
                  <span className="truncate">{p}</span>
                  <Send className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600 shrink-0 ml-2" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id || i}
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} animate-slideUp`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center shrink-0 shadow-xs mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[90%] sm:max-w-2xl rounded-2xl p-4 sm:p-5 text-xs sm:text-sm leading-relaxed shadow-xs ${
                    isUser
                      ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-tr-none'
                      : 'bg-white border border-slate-200/90 text-slate-800 rounded-tl-none space-y-3.5 shadow-xs'
                  }`}
                >
                  {/* Message Content */}
                  {isUser ? (
                    <div className="whitespace-pre-wrap font-medium">{msg.content}</div>
                  ) : (
                    <FormattedAssistantMessage content={msg.content} />
                  )}

                  {/* Assistant Citations & Action Bar */}
                  {!isUser && (
                    <div className="space-y-3 pt-2 border-t border-slate-200/60">
                      {/* Citations list */}
                      <div className="flex flex-wrap items-center gap-1.5">
                        {msg.citations && msg.citations.length > 0 ? (
                          <>
                            <span className="text-[11px] font-bold text-slate-400 mr-1">Sources:</span>
                            {msg.citations.map((c, idx) => (
                              <CitationBadge
                                key={idx}
                                pageNumber={c.page_number}
                                excerpt={c.excerpt}
                                relevanceScore={c.relevance_score}
                              />
                            ))}
                          </>
                        ) : (
                          <span className="text-[11px] text-slate-400 italic">No specific page citation</span>
                        )}
                      </div>

                      {/* Working Actions Bar */}
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <button
                          onClick={() => handleCopy(msg.content, msg.id || i)}
                          className="px-2 py-1 rounded-lg bg-white border border-slate-200 text-[11px] font-semibold text-slate-600 hover:bg-slate-100 transition flex items-center gap-1"
                          title="Copy Answer"
                        >
                          {copiedId === (msg.id || i) ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
                          <span>{copiedId === (msg.id || i) ? 'Copied' : 'Copy'}</span>
                        </button>

                        <button
                          onClick={() => handleAction('explain_more')}
                          className="px-2 py-1 rounded-lg bg-indigo-50 border border-indigo-200 text-[11px] font-semibold text-indigo-700 hover:bg-indigo-100 transition flex items-center gap-1"
                        >
                          <BookOpen className="w-3 h-3" />
                          <span>Explain More</span>
                        </button>

                        <button
                          onClick={() => handleAction('give_example')}
                          className="px-2 py-1 rounded-lg bg-purple-50 border border-purple-200 text-[11px] font-semibold text-purple-700 hover:bg-purple-100 transition flex items-center gap-1"
                        >
                          <Lightbulb className="w-3 h-3" />
                          <span>Give Example</span>
                        </button>

                        <button
                          onClick={() => handleAction('make_shorter')}
                          className="px-2 py-1 rounded-lg bg-slate-100 border border-slate-200 text-[11px] font-semibold text-slate-600 hover:bg-slate-200 transition flex items-center gap-1"
                        >
                          <Scissors className="w-3 h-3" />
                          <span>Shorter</span>
                        </button>

                        <button
                          onClick={() => handleAction('step_by_step')}
                          className="px-2 py-1 rounded-lg bg-blue-50 border border-blue-200 text-[11px] font-semibold text-blue-700 hover:bg-blue-100 transition flex items-center gap-1"
                        >
                          <GraduationCap className="w-3 h-3" />
                          <span>Step-by-Step</span>
                        </button>

                        <button
                          onClick={() => handleAction('ask_question')}
                          className="px-2 py-1 rounded-lg bg-rose-50 border border-rose-200 text-[11px] font-semibold text-rose-700 hover:bg-rose-100 transition flex items-center gap-1"
                        >
                          <HelpCircle className="w-3 h-3" />
                          <span>Test Me</span>
                        </button>

                        <button
                          onClick={() => handleAction(language === 'Hinglish' ? 'in_hindi' : 'in_hinglish')}
                          className="px-2 py-1 rounded-lg bg-amber-50 border border-amber-200 text-[11px] font-semibold text-amber-800 hover:bg-amber-100 transition flex items-center gap-1"
                        >
                          <Languages className="w-3 h-3" />
                          <span>{language === 'Hinglish' ? 'In Hindi 🇮🇳' : 'In Hinglish 🇮🇳'}</span>
                        </button>

                        <button
                          onClick={() => handleAction('generate_quiz')}
                          className="px-2 py-1 rounded-lg bg-teal-50 border border-teal-200 text-[11px] font-semibold text-teal-800 hover:bg-teal-100 transition flex items-center gap-1"
                          title="Generate Practice Quiz from this topic"
                        >
                          <QuestionIcon className="w-3 h-3" />
                          <span>Quiz</span>
                        </button>

                        <button
                          onClick={() => handleAction('create_flashcards')}
                          className="px-2 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-[11px] font-semibold text-emerald-800 hover:bg-emerald-100 transition flex items-center gap-1"
                          title="Generate Flashcards from this topic"
                        >
                          <Layers className="w-3 h-3" />
                          <span>Cards</span>
                        </button>
                      </div>

                      {/* Interactive Follow-up Suggestion Chips */}
                      {msg.follow_up_suggestions && msg.follow_up_suggestions.length > 0 && (
                        <div className="pt-2 border-t border-slate-200/40">
                          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                            Suggested Next Steps:
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.follow_up_suggestions.map((suggestion, sIdx) => (
                              <button
                                key={sIdx}
                                onClick={() => handleSend(suggestion)}
                                className="px-2.5 py-1 rounded-full bg-indigo-50/80 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-[11px] font-medium transition flex items-center gap-1"
                              >
                                <span>{suggestion}</span>
                                <ArrowRight className="w-2.5 h-2.5 text-indigo-500" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 text-xs font-bold mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="flex gap-3 justify-start animate-fadeIn">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200/90 rounded-2xl rounded-tl-none p-4 text-xs text-slate-600 flex items-center gap-2 shadow-xs">
              <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
              <span>Personal AI Tutor is thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Input Area */}
      <div className="p-3 sm:p-4 border-t border-slate-100 bg-white">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask your tutor anything (e.g. 'What is data modelling?', 'Explain in simple words')..."
            disabled={loading}
            className="flex-1 px-4 py-2.5 sm:py-3 text-xs sm:text-sm rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none transition"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="p-2.5 sm:px-5 sm:py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-50 text-white rounded-xl font-bold text-xs sm:text-sm shadow-md transition flex items-center gap-1.5 shrink-0"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Ask Tutor</span>
          </button>
        </form>
      </div>
    </div>
  );
}
