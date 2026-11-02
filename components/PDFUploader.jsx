import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles, X, ShieldCheck } from 'lucide-react';
import { api } from '../api';
import { useToast } from '../context/ToastContext';

export default function PDFUploader({ onUploadSuccess, onClose }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0); // 0: Idle, 1: Uploading, 2: Extracting, 3: Chunking & Embeddings, 4: Storing in ChromaDB, 5: Ready
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const toast = useToast();

  const steps = [
    { title: 'Upload PDF', desc: 'Secure transfer to local server' },
    { title: 'Text Extraction', desc: 'Page-by-page OCR & text parsing' },
    { title: 'Chunking & Embeddings', desc: 'Semantic dense vectorization' },
    { title: 'ChromaDB Indexing', desc: 'Persistent vector database storage' },
    { title: 'Ready for AI Chat', desc: 'Grounded RAG pipeline active' }
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (selectedFile) => {
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF document (.pdf).');
      return;
    }
    if (selectedFile.size > 25 * 1024 * 1024) {
      setError('File size exceeds 25MB limit.');
      return;
    }
    setError(null);
    setFile(selectedFile);
  };

  const startUpload = async () => {
    if (!file || uploading) return;
    setUploading(true);
    setError(null);
    setCurrentStep(1);

    // Simulated progress indicators for user reassurance
    const timer1 = setTimeout(() => setCurrentStep(2), 700);
    const timer2 = setTimeout(() => setCurrentStep(3), 1600);
    const timer3 = setTimeout(() => setCurrentStep(4), 2500);

    try {
      const res = await api.uploadDocument(file);
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setCurrentStep(5);
      toast.success(`'${file.name}' indexed successfully!`);

      setTimeout(() => {
        if (onUploadSuccess) onUploadSuccess(res.document);
      }, 700);
    } catch (err) {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      setError(err.message || 'Failed to process and index PDF.');
      toast.error(err.message || 'Upload failed');
      setCurrentStep(0);
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-slate-100 relative animate-scaleUp">
      {/* Close Button */}
      {!uploading && (
        <button
          onClick={onClose}
          className="absolute right-5 top-5 p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>
      )}

      {/* Header */}
      <div className="text-center mb-6">
        <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-3 shadow-xs">
          <Upload className="w-6 h-6" />
        </div>
        <h3 className="text-lg font-extrabold text-slate-900 tracking-tight">Upload Course PDF</h3>
        <p className="text-xs text-slate-500 mt-1">
          Lecture notes, chapters, papers, or course slides (up to 25MB)
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-2.5 text-xs text-rose-700 animate-slideUp">
          <AlertCircle className="w-4 h-4 text-rose-500 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!uploading ? (
        <div className="space-y-5">
          {/* Dropzone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
              dragActive
                ? 'border-indigo-500 bg-indigo-50/70 scale-[1.01]'
                : file
                ? 'border-emerald-400 bg-emerald-50/40'
                : 'border-slate-200 hover:border-indigo-400 hover:bg-slate-50/70'
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf"
              onChange={handleChange}
              className="hidden"
            />

            {file ? (
              <div className="space-y-2">
                <FileText className="w-10 h-10 text-emerald-600 mx-auto" />
                <p className="text-xs font-bold text-slate-900 truncate max-w-xs mx-auto">
                  {file.name}
                </p>
                <p className="text-[11px] text-slate-400">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready for processing
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-8 h-8 text-slate-400 mx-auto" />
                <p className="text-xs font-bold text-slate-700">
                  Drag and drop your PDF here, or <span className="text-indigo-600">browse</span>
                </p>
                <p className="text-[11px] text-slate-400">Supports standard text and OCR-extracted PDFs</p>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
            >
              Cancel
            </button>
            <button
              onClick={startUpload}
              disabled={!file}
              className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 disabled:opacity-40 text-white text-xs font-bold shadow-md shadow-indigo-200 transition flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Start Indexing</span>
            </button>
          </div>
        </div>
      ) : (
        /* Animated Multi-Step Processing Pipeline */
        <div className="space-y-5 py-2">
          <div className="space-y-3">
            {steps.map((st, idx) => {
              const stepNum = idx + 1;
              const isDone = currentStep > stepNum;
              const isCurrent = currentStep === stepNum;

              return (
                <div
                  key={idx}
                  className={`flex items-center gap-3 p-3 rounded-xl border text-xs transition-all ${
                    isCurrent
                      ? 'bg-indigo-50/70 border-indigo-200 font-bold text-indigo-900 shadow-xs'
                      : isDone
                      ? 'bg-emerald-50/40 border-emerald-100 text-slate-700'
                      : 'bg-slate-50/50 border-slate-100 text-slate-400'
                  }`}
                >
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-indigo-600 animate-spin shrink-0" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-slate-300 text-[10px] flex items-center justify-center text-slate-400 shrink-0">
                      {stepNum}
                    </div>
                  )}

                  <div className="overflow-hidden">
                    <p className="font-bold leading-tight">{st.title}</p>
                    <p className="text-[11px] text-slate-400 font-normal">{st.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="text-center pt-2">
            <span className="text-[11px] font-semibold text-slate-400 animate-pulse">
              Please wait while PyPDF extracts pages and ChromaDB indexes vectors...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
