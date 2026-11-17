import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import SummaryPage from './pages/SummaryPage';
import LearningPage from './pages/LearningPage';
import FileUpload from './components/FileUpload';
import api from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('study-mate-dark-mode') === 'true');
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const fetchAllData = async () => {
    try {
      const [docsData, statsData, healthData] = await Promise.allSettled([
        api.getDocuments(),
        api.getStats(),
        api.getHealth(),
      ]);

      if (docsData.status === 'fulfilled') setDocuments(docsData.value.documents || []);
      if (statsData.status === 'fulfilled') setStats(statsData.value);
      if (healthData.status === 'fulfilled') setHealth(healthData.value);
    } catch (err) {
      console.error('Error fetching data:', err);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  useEffect(() => {
    localStorage.setItem('study-mate-dark-mode', String(darkMode));
  }, [darkMode]);

  useEffect(() => {
    let lastTick = Date.now();
    const timer = window.setInterval(() => {
      const now = Date.now();
      if (document.visibilityState === 'visible') {
        const activeSeconds = Math.floor((now - lastTick) / 1000);
        if (activeSeconds > 0) {
          api.recordStudyTime(activeSeconds).catch((error) => console.error('Could not record study time:', error));
        }
      }
      lastTick = now;
    }, 60000);
    return () => window.clearInterval(timer);
  }, []);

  const handleNavigateToChat = (docId = null) => {
    setSelectedDocId(docId);
    setActiveTab('chat');
  };

  const handleNavigateToSummary = (docId = null) => {
    setSelectedDocId(docId);
    setActiveTab('summary');
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await api.deleteDocument(docId);
      await fetchAllData();
      if (selectedDocId === docId) {
        setSelectedDocId(null);
      }
    } catch (err) {
      console.error('Failed to delete document:', err);
      alert(err.response?.data?.detail || 'Failed to delete document.');
    }
  };

  const getPageHeader = () => {
    switch (activeTab) {
      case 'dashboard':
        return {
          title: 'Dashboard Overview',
          subtitle: 'Welcome to your RAG-powered intelligent study notes assistant.',
        };
      case 'chat':
        return {
          title: 'AI Study Assistant',
          subtitle: 'Ask questions and receive strictly grounded answers with page references.',
        };
      case 'documents':
        return {
          title: 'Study Materials',
          subtitle: 'Manage indexed PDF notes, slides, and textbooks.',
        };
      case 'summary':
        return {
          title: 'AI Study Summaries',
          subtitle: 'High-yield overviews, key concepts, and exam review points.',
        };
      case 'quiz':
        return { title: 'AI Quiz Generator', subtitle: 'Practice with document-grounded questions and review explanations.' };
      case 'flashcards':
        return { title: 'Smart Flashcards', subtitle: 'Review saved cards generated from your PDF materials.' };
      case 'mindmap':
        return { title: 'AI Mind Maps', subtitle: 'Explore topics and relationships extracted from your documents.' };
      case 'planner':
        return { title: 'AI Study Planner', subtitle: 'Build a revision plan and track completed topics.' };
      case 'analytics':
        return { title: 'Learning Analytics', subtitle: 'Track quiz performance, revision progress, and study time.' };
      default:
        return { title: 'Study Mate AI', subtitle: 'Intelligent Study Notes Assistant' };
    }
  };

  const headerInfo = getPageHeader();

  return (
    <div className={`app-shell flex h-screen overflow-hidden font-sans ${darkMode ? 'dark-mode' : ''}`}>
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        stats={stats}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={headerInfo.title}
          subtitle={headerInfo.subtitle}
          health={health}
          onOpenUpload={() => setShowUploadModal(true)}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode((value) => !value)}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'dashboard' && (
              <Dashboard
                stats={stats}
                documents={documents}
                onRefresh={fetchAllData}
                onNavigateToChat={handleNavigateToChat}
                onNavigateToSummary={handleNavigateToSummary}
                onDeleteDocument={handleDeleteDocument}
              />
            )}

            {activeTab === 'chat' && (
              <ChatPage
                documents={documents}
                selectedDocId={selectedDocId}
                onSelectDocId={setSelectedDocId}
                onNavigateToUpload={() => setShowUploadModal(true)}
              />
            )}

            {activeTab === 'documents' && (
              <DocumentsPage
                documents={documents}
                onRefresh={fetchAllData}
                onChatWithDoc={handleNavigateToChat}
                onSummarizeDoc={handleNavigateToSummary}
                onDeleteDocument={handleDeleteDocument}
              />
            )}

            {activeTab === 'summary' && (
              <SummaryPage
                documents={documents}
                preSelectedDocId={selectedDocId}
              />
            )}
            {['quiz', 'flashcards', 'mindmap', 'planner', 'analytics'].includes(activeTab) && (
              <LearningPage
                feature={activeTab}
                onNavigate={setActiveTab}
                documents={documents}
              />
            )}
          </div>
        </main>
      </div>

      {/* Upload Modal (Global quick action) */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="w-full max-w-xl">
            <FileUpload
              onUploadSuccess={() => {
                fetchAllData();
                setShowUploadModal(false);
              }}
              onClose={() => setShowUploadModal(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

