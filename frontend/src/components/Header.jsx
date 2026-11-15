import React from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, ShieldCheck } from 'lucide-react';

export default function Header({ title, subtitle, health, onOpenUpload }) {
  const isHealthy = health?.status === 'healthy';
  const hasGemini = health?.gemini_configured;

  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
      <div>
        <h2 className="text-xl font-bold text-slate-800 tracking-tight">{title}</h2>
        <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Gemini Status indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border bg-slate-50">
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
              hasGemini ? 'bg-emerald-400' : 'bg-amber-400'
            }`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${
              hasGemini ? 'bg-emerald-500' : 'bg-amber-500'
            }`}></span>
          </span>
          <span className="text-slate-600">
            {hasGemini ? 'Gemini AI Ready' : 'Add Gemini API Key in .env'}
          </span>
        </div>

        {/* Quick Upload Button */}
        {onOpenUpload && (
          <button
            onClick={onOpenUpload}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow-sm shadow-blue-500/20 transition-all hover:shadow"
          >
            <UploadCloud className="h-4 w-4" />
            <span>Upload PDF</span>
          </button>
        )}
      </div>
    </header>
  );
}

