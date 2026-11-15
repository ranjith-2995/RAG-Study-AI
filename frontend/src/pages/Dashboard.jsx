import React from 'react';
import { 
  FileText, 
  Layers, 
  Database, 
  Bot, 
  UploadCloud, 
  ArrowRight, 
  CheckCircle2, 
  Sparkles,
  BookOpen
} from 'lucide-react';
import StatCard from '../components/StatCard';
import FileUpload from '../components/FileUpload';
import DocumentCard from '../components/DocumentCard';

export default function Dashboard({ 
  stats, 
  documents, 
  onRefresh, 
  onNavigateToChat, 
  onNavigateToSummary, 
  onDeleteDocument 
}) {
  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 rounded-2xl p-7 text-white shadow-lg shadow-blue-500/10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm text-xs font-medium border border-white/20">
            <Sparkles className="h-3.5 w-3.5 text-blue-200" />
            <span>AI-Powered Study Intelligence</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight">
            Master your study notes with Retrieval-Augmented Generation
          </h2>
          <p className="text-blue-100 text-xs sm:text-sm leading-relaxed">
            Upload your lecture slides, textbooks, or syllabus PDFs. STUDY MATE AI extracts, embeds, and indexes your notes so you can chat directly with your course material without hallucinated answers.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => onNavigateToChat()}
            className="px-5 py-2.5 bg-white text-blue-700 hover:bg-blue-50 font-semibold text-xs rounded-xl shadow transition-all flex items-center justify-center gap-2"
          >
            <span>Open AI Chat</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Stats Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Uploaded Documents"
          value={stats?.total_documents ?? documents.length}
          subtitle="Processed PDF files"
          icon={FileText}
          color="blue"
        />
        <StatCard
          title="Indexed Chunks"
          value={stats?.total_chunks ?? 0}
          subtitle="Searchable vector segments"
          icon={Layers}
          color="indigo"
        />
        <StatCard
          title="FAISS Vector Store"
          value={stats?.vector_index_ready ? 'Ready' : 'Standby'}
          subtitle="Local L2 similarity search"
          icon={Database}
          color="emerald"
        />
        <StatCard
          title="AI Generator"
          value="Gemini 1.5"
          subtitle="Ground-truth answering"
          icon={Bot}
          color="purple"
        />
      </div>

      {/* RAG Workflow Visual Explanation */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Database className="h-4 w-4 text-blue-600" />
          <span>How Study Mate RAG Works</span>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-mono text-blue-600 font-bold block mb-1">STEP 1</span>
            <p className="font-semibold text-slate-800">PDF Ingestion</p>
            <p className="text-slate-500 mt-1">PyPDF extracts full-text page-by-page from study notes.</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-mono text-blue-600 font-bold block mb-1">STEP 2</span>
            <p className="font-semibold text-slate-800">Text Chunking</p>
            <p className="text-slate-500 mt-1">Splits text into ~800 char chunks with page metadata.</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-mono text-blue-600 font-bold block mb-1">STEP 3</span>
            <p className="font-semibold text-slate-800">Vector Embeddings</p>
            <p className="text-slate-500 mt-1">Sentence Transformers generates 384-dim dense vectors.</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
            <span className="font-mono text-blue-600 font-bold block mb-1">STEP 4</span>
            <p className="font-semibold text-slate-800">FAISS Similarity Search</p>
            <p className="text-slate-500 mt-1">Retrieves top-k closest chunks matching your question.</p>
          </div>
          <div className="p-3 bg-blue-50/70 rounded-xl border border-blue-200">
            <span className="font-mono text-blue-700 font-bold block mb-1">STEP 5</span>
            <p className="font-semibold text-blue-900">Gemini Synthesis</p>
            <p className="text-blue-700 mt-1">Generates answers strictly from context with page citations.</p>
          </div>
        </div>
      </div>

      {/* Main Grid: Upload + Recent Documents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <FileUpload onUploadSuccess={onRefresh} />
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-slate-800">Recent Study Materials</h3>
              <p className="text-xs text-slate-500">Manage and chat with your uploaded PDF documents.</p>
            </div>
            <span className="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full font-medium">
              {documents.length} Total
            </span>
          </div>

          {documents.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-3">
              <div className="h-12 w-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
                <BookOpen className="h-6 w-6" />
              </div>
              <h4 className="text-sm font-semibold text-slate-700">No documents uploaded yet</h4>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Upload your first study document using the upload box on the left to start asking questions.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.slice(0, 4).map((doc) => (
                <DocumentCard
                  key={doc.id}
                  doc={doc}
                  onChatWithDoc={onNavigateToChat}
                  onSummarizeDoc={onNavigateToSummary}
                  onDeleteDoc={onDeleteDocument}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

