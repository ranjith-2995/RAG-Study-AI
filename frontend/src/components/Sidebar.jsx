import React from 'react';
import { 
  BookOpen, 
  MessageSquare, 
  FileText, 
  Sparkles, 
  LayoutDashboard,
  BrainCircuit,
  GraduationCap
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, stats }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'chat', label: 'AI Chat Assistant', icon: MessageSquare },
    { id: 'documents', label: 'Study Materials', icon: FileText, badge: stats?.total_documents },
    { id: 'summary', label: 'AI Summaries', icon: Sparkles },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col shrink-0 min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <GraduationCap className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight tracking-tight text-white flex items-center gap-1.5">
            STUDY MATE <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-semibold border border-blue-500/30">AI</span>
          </h1>
          <p className="text-xs text-slate-400">Intelligent Notes Assistant</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1.5">
        <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Workspace
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  isActive ? 'bg-blue-700 text-white' : 'bg-slate-800 text-slate-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* RAG Engine Status Info */}
      <div className="p-4 m-3 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs">
        <div className="flex items-center gap-2 mb-2 text-blue-400 font-medium">
          <BrainCircuit className="h-4 w-4" />
          <span>RAG Pipeline Architecture</span>
        </div>
        <div className="space-y-1 text-slate-400">
          <div className="flex justify-between">
            <span>Embeddings:</span>
            <span className="text-slate-200 font-mono text-[11px]">all-MiniLM-L6-v2</span>
          </div>
          <div className="flex justify-between">
            <span>Vector Store:</span>
            <span className="text-slate-200 font-mono text-[11px]">FAISS</span>
          </div>
          <div className="flex justify-between">
            <span>Generator:</span>
            <span className="text-slate-200 font-mono text-[11px]">Google Gemini</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
        Study Mate AI • RAG Project
      </div>
    </aside>
  );
}

