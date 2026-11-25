import React, { useState, useEffect } from 'react';
import {
  Layers,
  Sparkles,
  RotateCw,
  CheckCircle2,
  XCircle,
  Shuffle,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  FileText,
  Loader2,
  HelpCircle,
  Award
} from 'lucide-react';
import { api } from '../api';
import CitationBadge from '../components/CitationBadge';
import { useToast } from '../context/ToastContext';

export default function FlashcardsPage({ activeDocId, documents = [] }) {
  const [deck, setDeck] = useState({ cards: [], total: 0, mastered: 0, learning: 0, mastery_percentage: 0 });
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generateCount, setGenerateCount] = useState(8);
  const [customTopic, setCustomTopic] = useState('');
  const toast = useToast();

  const selectedDoc = documents.find((d) => d.id === Number(activeDocId));

  const loadFlashcards = async () => {
    if (!activeDocId) return;
    setLoading(true);
    try {
      const data = await api.getFlashcards(activeDocId);
      // Compute mastery counters
      const cards = data.cards || [];
      const mastered = cards.filter((c) => c.status === 'known' || c.mastery_status === 'mastered').length;
      const total = cards.length;
      const percent = total > 0 ? Math.round((mastered / total) * 100) : 0;

      setDeck({
        cards,
        total,
        mastered,
        learning: total - mastered,
        mastery_percentage: percent
      });
      setCurrentIndex(0);
      setIsFlipped(false);
    } catch (err) {
      console.error('Failed to load flashcards:', err);
      toast.error('Failed to load flashcards');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFlashcards();
  }, [activeDocId]);

  // Keyboard navigation for power studying: Space = flip, Left = Prev, Right = Next
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.code === 'Space') {
        e.preventDefault();
        setIsFlipped((prev) => !prev);
      } else if (e.code === 'ArrowRight') {
        handleNext();
      } else if (e.code === 'ArrowLeft') {
        handlePrev();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [deck.cards.length, currentIndex]);

  const handleGenerateMore = async () => {
    if (!activeDocId) return;
    setGenerating(true);
    try {
      const topicParam = customTopic.trim() ? customTopic.trim() : null;
      const res = await api.generateFlashcards(activeDocId, generateCount, topicParam);
      toast.success(`Generated ${res.cards?.length || generateCount} new active recall flashcards via Gemini!`);
      loadFlashcards();
    } catch (err) {
      toast.error(err.message || 'Failed to generate flashcards.');
    } finally {
      setGenerating(false);
    }
  };

  const handleMastery = async (newStatus) => {
    const currentCard = deck.cards[currentIndex];
    if (!currentCard) return;

    try {
      await api.updateFlashcardMastery(currentCard.id, newStatus);
      const updatedCards = [...deck.cards];
      updatedCards[currentIndex].status = newStatus === 'mastered' ? 'known' : 'review';
      updatedCards[currentIndex].mastery_status = newStatus;

      const masteredCount = updatedCards.filter(
        (c) => c.status === 'known' || c.mastery_status === 'mastered'
      ).length;

      setDeck({
        ...deck,
        cards: updatedCards,
        mastered: masteredCount,
        learning: updatedCards.length - masteredCount,
        mastery_percentage: Math.round((masteredCount / updatedCards.length) * 100)
      });

      toast.success(newStatus === 'mastered' ? 'Marked as Mastered ⭐' : 'Saved for Review 📖');

      // Smooth advance to next card
      if (currentIndex < deck.cards.length - 1) {
        setIsFlipped(false);
        setTimeout(() => setCurrentIndex((prev) => prev + 1), 200);
      }
    } catch (err) {
      toast.error(err.message || 'Failed to update card status');
    }
  };

  const handleShuffle = () => {
    const shuffled = [...deck.cards].sort(() => Math.random() - 0.5);
    setDeck({ ...deck, cards: shuffled });
    setCurrentIndex(0);
    setIsFlipped(false);
    toast.info('Deck shuffled randomly 🔀');
  };

  const handleNext = () => {
    if (currentIndex < deck.cards.length - 1) {
      setIsFlipped(false);
      setTimeout(() => setCurrentIndex((prev) => prev + 1), 100);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setIsFlipped(false);
      setTimeout(() => setCurrentIndex((prev) => prev - 1), 100);
    }
  };

  const currentCard = deck.cards[currentIndex];
  const total = deck.cards.length;

  if (!selectedDoc) {
    return (
      <div className="p-12 text-center bg-white rounded-3xl border border-slate-200/80 shadow-sm max-w-xl mx-auto mt-10">
        <Layers className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <h3 className="text-base font-bold text-slate-800">No Document Selected</h3>
        <p className="text-xs text-slate-500 mt-1">Please select or upload a document to practice active recall flashcards.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto animate-fadeIn">
      {/* Top Header Bar */}
      <div className="bg-white p-5 sm:p-6 rounded-3xl border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold uppercase tracking-wider">
              Active Recall Deck
            </span>
            <span className="text-xs text-slate-400">
              {selectedDoc.original_filename || selectedDoc.original_name}
            </span>
          </div>
          <h2 className="text-xl font-extrabold text-slate-900 tracking-tight">
            3D Spaced Repetition Study Cards
          </h2>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap items-center gap-2 self-stretch sm:self-center">
          <input
            type="text"
            value={customTopic}
            onChange={(e) => setCustomTopic(e.target.value)}
            placeholder="Focus Topic / Chapter (Optional)"
            className="px-3 py-1.5 text-xs font-medium rounded-xl bg-slate-50 border border-slate-200 text-slate-700 outline-none w-full sm:w-44 placeholder:text-slate-400"
          />

          <select
            value={generateCount}
            onChange={(e) => setGenerateCount(Number(e.target.value))}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-slate-50 border border-slate-200 text-slate-700 outline-none cursor-pointer"
          >
            <option value={5}>5 Cards</option>
            <option value={8}>8 Cards</option>
            <option value={12}>12 Cards</option>
            <option value={16}>16 Cards</option>
            <option value={20}>20 Cards</option>
            <option value={25}>25 Cards</option>
          </select>

          <button
            onClick={handleShuffle}
            disabled={total === 0}
            className="p-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-600 transition"
            title="Shuffle Deck"
          >
            <Shuffle className="w-4 h-4" />
          </button>

          <button
            onClick={handleGenerateMore}
            disabled={generating}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-1.5 shrink-0"
          >
            {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>{generating ? 'Generating...' : 'Add Cards'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200/80 shadow-xs">
          <Loader2 className="w-8 h-8 text-emerald-600 animate-spin mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-500">Loading flashcard deck...</p>
        </div>
      ) : total === 0 ? (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto shadow-xs">
            <Layers className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">No Flashcards in this Deck</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto leading-relaxed">
              Auto-generate spaced repetition cards to memorize key definitions, algorithms, and formulas.
            </p>
          </div>
          <button
            onClick={handleGenerateMore}
            disabled={generating}
            className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white text-xs font-bold rounded-xl shadow-md transition inline-flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Generate Study Cards</span>
          </button>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Deck Progress Bar */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-slate-600">
                Card {currentIndex + 1} of {total}
              </span>
              <div className="flex items-center gap-3">
                <span className="text-emerald-600">⭐ {deck.mastered} Mastered</span>
                <span className="text-amber-600">📖 {deck.learning} In Review</span>
                <span className="text-slate-400 font-normal">({deck.mastery_percentage}%)</span>
              </div>
            </div>

            <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden flex">
              <div
                className="h-full bg-emerald-500 transition-all duration-300"
                style={{ width: `${deck.mastery_percentage}%` }}
              />
              <div
                className="h-full bg-amber-400 transition-all duration-300"
                style={{ width: `${100 - deck.mastery_percentage}%` }}
              />
            </div>
          </div>

          {/* 3D Interactive Flashcard */}
          <div
            onClick={() => setIsFlipped(!isFlipped)}
            className="perspective-1000 min-h-[300px] sm:min-h-[340px] cursor-pointer group select-none"
          >
            <div
              className={`relative w-full h-full min-h-[300px] sm:min-h-[340px] rounded-3xl p-6 sm:p-8 border shadow-lg transition-transform duration-500 transform-style-3d ${
                isFlipped ? 'rotate-y-180 bg-slate-900 text-white border-slate-800' : 'bg-white text-slate-900 border-slate-200/90'
              }`}
            >
              {/* Front Side: Question / Prompt */}
              <div className={`absolute inset-0 p-6 sm:p-8 flex flex-col justify-between backface-hidden ${isFlipped ? 'hidden' : 'flex'}`}>
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-[10px] font-bold uppercase tracking-wider">
                    {currentCard.topic || 'Core Concept'}
                  </span>
                  {currentCard.page_number && (
                    <span className="text-xs font-semibold text-slate-400">
                      Page {currentCard.page_number}
                    </span>
                  )}
                </div>

                <div className="my-auto py-4 text-center">
                  <h3 className="text-lg sm:text-xl font-extrabold text-slate-900 leading-snug">
                    {currentCard.question || currentCard.front}
                  </h3>
                </div>

                <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 font-medium group-hover:text-indigo-600 transition">
                  <RotateCw className="w-3.5 h-3.5" />
                  <span>Click or press Spacebar to reveal definition</span>
                </div>
              </div>

              {/* Back Side: Answer / Definition */}
              <div className={`absolute inset-0 p-6 sm:p-8 flex flex-col justify-between rotate-y-180 backface-hidden ${isFlipped ? 'flex' : 'hidden'}`}>
                <div className="flex items-center justify-between">
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-400/20 text-emerald-300 text-[10px] font-bold uppercase tracking-wider">
                    Verified Answer
                  </span>
                  {currentCard.page_number && (
                    <span className="text-xs font-semibold text-slate-400">
                      Page {currentCard.page_number} Provenance
                    </span>
                  )}
                </div>

                <div className="my-auto py-4 text-center">
                  <p className="text-sm sm:text-base text-slate-100 leading-relaxed font-normal">
                    {currentCard.answer || currentCard.back}
                  </p>
                </div>

                <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 font-medium">
                  <RotateCw className="w-3.5 h-3.5" />
                  <span>Click to flip back</span>
                </div>
              </div>
            </div>
          </div>

          {/* Controls: Next / Prev + Mastery Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
            {/* Prev / Next Buttons */}
            <div className="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-start">
              <button
                onClick={handlePrev}
                disabled={currentIndex === 0}
                className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-40 text-slate-700 text-xs font-bold transition flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Prev</span>
              </button>

              <button
                onClick={handleNext}
                disabled={currentIndex === total - 1}
                className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-40 text-slate-700 text-xs font-bold transition flex items-center gap-1"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Mastery State Toggles */}
            <div className="flex items-center gap-2.5 w-full sm:w-auto">
              <button
                onClick={() => handleMastery('learning')}
                className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-800 text-xs font-bold transition flex items-center justify-center gap-1.5"
              >
                <XCircle className="w-4 h-4 text-amber-600" />
                <span>Still Learning</span>
              </button>

              <button
                onClick={() => handleMastery('mastered')}
                className="flex-1 sm:flex-none px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition flex items-center justify-center gap-1.5"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Mastered</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
