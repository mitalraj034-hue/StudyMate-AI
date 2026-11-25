import React, { useState, useEffect } from 'react';
import {
  FileText,
  Search,
  Upload,
  Trash2,
  BookOpen,
  MessageSquare,
  HelpCircle,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  Clock,
  HardDrive,
  X
} from 'lucide-react';
import { api } from '../api';
import PDFUploader from '../components/PDFUploader';
import { useToast } from '../context/ToastContext';

export default function DocumentsPage({
  setActiveTab,
  activeDocId,
  setActiveDocId,
  isUploadOpen,
  setIsUploadOpen
}) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteConfirmDoc, setDeleteConfirmDoc] = useState(null);
  const toast = useToast();

  const fetchDocuments = async (query = '') => {
    try {
      const data = await api.getDocuments(query);
      setDocuments(data);
      if (data.length > 0 && !activeDocId) {
        setActiveDocId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
      toast.error('Failed to load study materials');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments(searchQuery);
  }, [searchQuery]);

  const handleDelete = async (docId) => {
    try {
      await api.deleteDocument(docId);
      toast.success('Document deleted successfully');
      setDeleteConfirmDoc(null);
      fetchDocuments(searchQuery);
      if (activeDocId === docId) {
        setActiveDocId(null);
      }
    } catch (err) {
      toast.error(err.message || 'Failed to delete document');
    }
  };

  const handleStudyAction = (docId, tab) => {
    setActiveDocId(docId);
    setActiveTab(tab);
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 KB';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fadeIn">
      {/* Top Search & Upload Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents by course title..."
            className="w-full pl-10 pr-4 py-2 text-xs rounded-xl border border-slate-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none transition"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <span className="text-xs font-semibold text-slate-400 mr-2">
            {documents.length} {documents.length === 1 ? 'material' : 'materials'} indexed
          </span>
          <button
            onClick={() => setIsUploadOpen(true)}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white text-xs font-bold rounded-xl shadow-md transition flex items-center gap-1.5"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload Course PDF</span>
          </button>
        </div>
      </div>

      {/* Documents Grid / List */}
      {loading ? (
        <div className="p-16 text-center bg-white rounded-3xl border border-slate-200/80">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-500">Loading study materials...</p>
        </div>
      ) : documents.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-3xl border border-slate-200/80 shadow-xs max-w-xl mx-auto space-y-4">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto shadow-xs">
            <FileText className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">No Study Materials Found</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto leading-relaxed">
              Upload your first syllabus reading, lecture slides, or textbook chapter to index embeddings into ChromaDB.
            </p>
          </div>
          <button
            onClick={() => setIsUploadOpen(true)}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md transition inline-flex items-center gap-1.5"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload PDF Now</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {documents.map((doc) => {
            const isSelected = doc.id === Number(activeDocId);
            const docName = doc.original_filename || doc.original_name || doc.filename;
            const pages = doc.page_count || doc.pages || 0;
            const chunks = doc.chunk_count || doc.chunks || 0;

            return (
              <div
                key={doc.id}
                className={`p-5 rounded-2xl bg-white border transition-all flex flex-col justify-between shadow-xs hover:shadow-md ${
                  isSelected
                    ? 'border-indigo-500 ring-2 ring-indigo-100'
                    : 'border-slate-200/80 hover:border-slate-300'
                }`}
              >
                <div>
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="p-3 rounded-xl bg-indigo-50 text-indigo-600 shrink-0">
                      <FileText className="w-6 h-6" />
                    </div>

                    <div className="flex items-center gap-1">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {doc.status === 'completed' || doc.status === 'ready' ? 'Indexed' : doc.status}
                      </span>
                      <button
                        onClick={() => setDeleteConfirmDoc(doc)}
                        className="p-1 text-slate-300 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition"
                        title="Delete document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Document Title & Metadata */}
                  <h4 className="font-bold text-slate-900 text-sm leading-snug line-clamp-2 mb-2" title={docName}>
                    {docName}
                  </h4>

                  <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-400 mb-4">
                    <span>{pages} Pages</span>
                    <span>•</span>
                    <span>{chunks} Chunks</span>
                    <span>•</span>
                    <span>{formatFileSize(doc.file_size)}</span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-1.5">
                  <button
                    onClick={() => handleStudyAction(doc.id, 'chat')}
                    className="flex-1 py-1.5 px-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold rounded-lg transition text-center"
                  >
                    AI Chat
                  </button>
                  <button
                    onClick={() => handleStudyAction(doc.id, 'quiz')}
                    className="flex-1 py-1.5 px-2 bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-bold rounded-lg transition text-center"
                  >
                    Quiz
                  </button>
                  <button
                    onClick={() => handleStudyAction(doc.id, 'flashcards')}
                    className="flex-1 py-1.5 px-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold rounded-lg transition text-center"
                  >
                    Cards
                  </button>
                  <button
                    onClick={() => handleStudyAction(doc.id, 'summaries')}
                    className="flex-1 py-1.5 px-2 bg-purple-50 hover:bg-purple-100 text-purple-700 text-xs font-bold rounded-lg transition text-center"
                  >
                    Summary
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-100 animate-scaleUp space-y-4">
            <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto">
              <Trash2 className="w-5 h-5" />
            </div>
            <div className="text-center">
              <h4 className="text-sm font-bold text-slate-900">Delete Study Material?</h4>
              <p className="text-xs text-slate-500 mt-1">
                Are you sure you want to delete <span className="font-semibold text-slate-800">"{deleteConfirmDoc.original_filename || deleteConfirmDoc.original_name}"</span>? All vector embeddings, quiz history, and flashcards will be removed.
              </p>
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={() => setDeleteConfirmDoc(null)}
                className="flex-1 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirmDoc.id)}
                className="flex-1 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition shadow-sm"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
