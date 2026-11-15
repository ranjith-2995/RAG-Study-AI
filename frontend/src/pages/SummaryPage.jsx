import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Sparkles, BookOpen, Layers, CheckCircle2, Copy, Check, Loader2, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function SummaryPage({ documents, preSelectedDocId }) {
  const [selectedDocId, setSelectedDocId] = useState(preSelectedDocId || '');
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (preSelectedDocId) {
      setSelectedDocId(preSelectedDocId);
      handleGenerateSummary(preSelectedDocId);
    }
  }, [preSelectedDocId]);

  const handleGenerateSummary = async (docIdToUse = selectedDocId) => {
    if (documents.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.getSummary(docIdToUse || null);
      setSummaryData(res);
    } catch (err) {
      console.error('Summary error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate study summary.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!summaryData) return;
    const textToCopy = `STUDY MATE AI SUMMARY: ${summaryData.filename}\n\n${summaryData.summary}\n\nKEY TOPICS:\n${summaryData.key_topics?.join('\n')}\n\nESSENTIAL STUDY POINTS:\n${summaryData.study_points?.join('\n')}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (documents.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center max-w-lg mx-auto my-12 space-y-4 shadow-sm">
        <div className="h-16 w-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto">
          <Sparkles className="h-8 w-8" />
        </div>
        <div className="space-y-1">
          <h3 className="text-lg font-bold text-slate-800">No Documents to Summarize</h3>
          <p className="text-xs text-slate-500">
            Please upload study materials first to generate AI study guides and key topics.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Selection Box */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <BookOpen className="h-5 w-5 text-indigo-600 shrink-0" />
          <div className="flex-1">
            <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Select Document to Summarize
            </label>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Uploaded Documents (Combined Overview)</option>
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename} ({doc.total_pages} pages)
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={() => handleGenerateSummary()}
          disabled={loading}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white text-xs font-semibold rounded-xl shadow-sm transition-all shrink-0"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analyzing Notes...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Generate AI Summary</span>
            </>
          )}
        </button>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-4 shadow-sm animate-pulse">
          <div className="h-12 w-12 rounded-full bg-indigo-50 text-indigo-600 mx-auto flex items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
          <div className="space-y-2">
            <h4 className="text-base font-semibold text-slate-800">Reading and synthesizing your study notes...</h4>
            <p className="text-xs text-slate-400">
              Extracting core concepts, identifying key formulas/theories, and structuring review points.
            </p>
          </div>
        </div>
      )}

      {/* Summary Results */}
      {summaryData && !loading && (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 uppercase tracking-wider">
                Study Guide Generated
              </span>
              <h3 className="text-lg font-bold text-slate-800 mt-1">
                {summaryData.filename || 'Comprehensive Notes Summary'}
              </h3>
            </div>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-indigo-600 bg-slate-50 hover:bg-indigo-50 px-3 py-1.5 rounded-lg border border-slate-200 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                  <span className="text-emerald-600 font-medium">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy Guide</span>
                </>
              )}
            </button>
          </div>

          {/* Key Topics Badges */}
          {summaryData.key_topics && summaryData.key_topics.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                <Layers className="h-4 w-4 text-indigo-600" />
                <span>Important Topics Covered</span>
              </h4>
              <div className="flex flex-wrap gap-2">
                {summaryData.key_topics.map((topic, i) => (
                  <span
                    key={i}
                    className="px-3 py-1.5 bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-lg font-medium"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Executive Overview */}
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Executive Overview
            </h4>
            <div className="prose prose-sm max-w-none prose-slate text-slate-700 leading-relaxed">
              <ReactMarkdown>{summaryData.summary}</ReactMarkdown>
            </div>
          </div>

          {/* Essential Study Points */}
          {summaryData.study_points && summaryData.study_points.length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span>Essential Study Points & Review Highlights</span>
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {summaryData.study_points.map((point, i) => (
                  <div key={i} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex items-start gap-3">
                    <span className="h-5 w-5 rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    <p className="text-xs text-slate-700 leading-relaxed">{point}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

