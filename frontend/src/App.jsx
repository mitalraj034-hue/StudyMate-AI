import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';
import { api } from './api';

import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import PDFUploader from './components/PDFUploader';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';

import DashboardPage from './pages/DashboardPage';
import DocumentsPage from './pages/DocumentsPage';
import ChatPage from './pages/ChatPage';
import SummariesPage from './pages/SummariesPage';
import QuizPage from './pages/QuizPage';
import FlashcardsPage from './pages/FlashcardsPage';
import ProgressPage from './pages/ProgressPage';
import ProfilePage from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';
import { useToast } from './context/ToastContext';

export default function App() {
  const { user, isAuthenticated, loading, login } = useAuth();
  const toast = useToast();
  
  // Public navigation view state ('landing', 'login', 'register', 'forgot')
  const [publicView, setPublicView] = useState('landing');
  
  // Authenticated workspace tab state
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Active documents state
  const [documents, setDocuments] = useState([]);
  const [activeDocId, setActiveDocId] = useState(null);

  const fetchDocs = async () => {
    if (!isAuthenticated) return;
    try {
      const data = await api.getDocuments();
      setDocuments(data);
      if (data.length > 0 && !activeDocId) {
        setActiveDocId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch documents in App:', err);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [isAuthenticated]);

  // Demo 1-click login handler
  const handleDemoLogin = async () => {
    try {
      await login('student@studymate.ai', 'password123');
      toast.success('Signed in as demo student (Alex Chen)');
    } catch (err) {
      toast.error('Demo user login failed: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-bold text-slate-500">Loading StudyMate AI...</p>
        </div>
      </div>
    );
  }

  // If not logged in, render Landing or Auth views
  if (!isAuthenticated) {
    if (publicView === 'login') {
      return (
        <LoginPage
          onNavigateRegister={() => setPublicView('register')}
          onNavigateForgot={() => setPublicView('forgot')}
          onNavigateHome={() => setPublicView('landing')}
        />
      );
    }
    if (publicView === 'register') {
      return (
        <RegisterPage
          onNavigateLogin={() => setPublicView('login')}
          onNavigateHome={() => setPublicView('landing')}
        />
      );
    }
    if (publicView === 'forgot') {
      return (
        <ForgotPasswordPage
          onNavigateLogin={() => setPublicView('login')}
          onNavigateHome={() => setPublicView('landing')}
        />
      );
    }
    return (
      <LandingPage
        onNavigateLogin={() => setPublicView('login')}
        onNavigateRegister={() => setPublicView('register')}
        onDemoLogin={handleDemoLogin}
      />
    );
  }

  // Page title mapping
  const titles = {
    dashboard: { title: 'Student Dashboard', subtitle: 'Overview of course documents, recent test scores and study velocity' },
    documents: { title: 'My Study Materials', subtitle: 'Manage, view and index your course PDFs' },
    chat: { title: 'AI Document Chat', subtitle: 'Grounded question answering with verified page citations' },
    summaries: { title: 'Smart Summaries', subtitle: 'Concise executive summaries and key concept breakdowns' },
    quiz: { title: 'MCQ Quiz Generator', subtitle: 'Practice tests created directly from your syllabus' },
    flashcards: { title: 'Active Recall Flashcards', subtitle: 'Master key definitions with 3D study cards' },
    progress: { title: 'Learning Progress & Analytics', subtitle: 'Track test scores and syllabus completion trends' },
    profile: { title: 'Student Profile', subtitle: 'Manage academic goals, degree major and account security' },
    settings: { title: 'Platform Settings', subtitle: 'AI provider keys and vector database configuration' }
  };

  const currentTitle = titles[activeTab] || { title: 'StudyMate AI', subtitle: '' };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isMobileOpen={isMobileOpen}
        setIsMobileOpen={setIsMobileOpen}
      />

      {/* Main Workspace Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64 transition-all duration-300">
        {/* Top Header */}
        <TopHeader
          title={currentTitle.title}
          subtitle={currentTitle.subtitle}
          documents={documents}
          activeDocId={activeDocId}
          setActiveDocId={setActiveDocId}
          onOpenUpload={() => setIsUploadOpen(true)}
          setIsMobileOpen={setIsMobileOpen}
        />

        {/* Content Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              setActiveTab={setActiveTab}
              onOpenUpload={() => setIsUploadOpen(true)}
              setActiveDocId={setActiveDocId}
            />
          )}

          {activeTab === 'documents' && (
            <DocumentsPage
              setActiveTab={setActiveTab}
              activeDocId={activeDocId}
              setActiveDocId={setActiveDocId}
              isUploadOpen={isUploadOpen}
              setIsUploadOpen={setIsUploadOpen}
            />
          )}

          {activeTab === 'chat' && (
            <ChatPage
              activeDocId={activeDocId}
              documents={documents}
              setActiveDocId={setActiveDocId}
            />
          )}

          {activeTab === 'summaries' && (
            <SummariesPage
              activeDocId={activeDocId}
              documents={documents}
            />
          )}

          {activeTab === 'quiz' && (
            <QuizPage
              activeDocId={activeDocId}
              documents={documents}
            />
          )}

          {activeTab === 'flashcards' && (
            <FlashcardsPage
              activeDocId={activeDocId}
              documents={documents}
            />
          )}

          {activeTab === 'progress' && (
            <ProgressPage
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'profile' && (
            <ProfilePage />
          )}

          {activeTab === 'settings' && (
            <SettingsPage />
          )}
        </main>
      </div>

      {/* Global PDF Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
          <PDFUploader
            onUploadSuccess={(newDoc) => {
              setIsUploadOpen(false);
              fetchDocs();
              if (newDoc?.id) setActiveDocId(newDoc.id);
            }}
            onClose={() => setIsUploadOpen(false)}
          />
        </div>
      )}
    </div>
  );
}
