import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import SummaryPage from './pages/SummaryPage';
import FileUpload from './components/FileUpload';
import api from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
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
      default:
        return { title: 'Study Mate AI', subtitle: 'Intelligent Study Notes Assistant' };
    }
  };

  const headerInfo = getPageHeader();

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
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

