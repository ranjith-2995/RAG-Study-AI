import React from 'react';
import { UploadCloud, Moon, Sun } from 'lucide-react';

export default function Header({ title, subtitle, health, onOpenUpload, darkMode, onToggleDarkMode }) {
  const isHealthy = health?.status === 'healthy';
  const hasGemini = health?.gemini_configured;

  return (
    <header className="app-header bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10 shadow-sm">
      <div>
        <h2 className="text-xl font-bold text-slate-800 tracking-tight">{title}</h2>
        <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={onToggleDarkMode}
          className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-100"
          aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          title={darkMode ? 'Light mode' : 'Dark mode'}
        >
          {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
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

