import React from 'react';
import ChatInterface from '../components/ChatInterface';
import { BookOpen, Sparkles, AlertCircle } from 'lucide-react';

export default function ChatPage({ documents, selectedDocId, onSelectDocId, onNavigateToUpload }) {
  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-lg mx-auto my-12 space-y-4 shadow-sm">
        <div className="h-16 w-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto">
          <BookOpen className="h-8 w-8" />
        </div>
        <div className="space-y-1">
          <h3 className="text-lg font-bold text-slate-800">No Study Materials Found</h3>
          <p className="text-xs text-slate-500">
            To ask questions, you must first upload at least one PDF textbook or lecture slide.
          </p>
        </div>
        <button
          onClick={onNavigateToUpload}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-sm transition-all"
        >
          Upload PDF Notes
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <ChatInterface
        documents={documents}
        selectedDocId={selectedDocId}
        onSelectDocId={onSelectDocId}
      />
    </div>
  );
}

