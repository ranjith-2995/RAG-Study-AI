import React, { useState } from 'react';
import { FileText, Calendar, Layers, HardDrive, Trash2, MessageSquare, Sparkles, AlertCircle } from 'lucide-react';

export default function DocumentCard({ doc, onChatWithDoc, onSummarizeDoc, onDeleteDoc }) {
  const [isDeleting, setIsDeleting] = useState(false);

  const formattedDate = new Date(doc.upload_time).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${doc.filename}"? This will also remove all its vectors from the FAISS database.`)) {
      setIsDeleting(true);
      try {
        await onDeleteDoc(doc.id);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
      <div>
        {/* Header with icon & badge */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <h4 className="font-semibold text-slate-800 text-sm leading-snug line-clamp-1" title={doc.filename}>
                {doc.filename}
              </h4>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                <Calendar className="h-3 w-3" />
                {formattedDate}
              </p>
            </div>
          </div>
          <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            {doc.status}
          </span>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100 text-xs">
          <div className="bg-slate-50 p-2 rounded-lg text-center">
            <p className="text-slate-400 text-[10px]">PAGES</p>
            <p className="font-semibold text-slate-700">{doc.total_pages}</p>
          </div>
          <div className="bg-slate-50 p-2 rounded-lg text-center">
            <p className="text-slate-400 text-[10px]">CHUNKS</p>
            <p className="font-semibold text-slate-700">{doc.total_chunks}</p>
          </div>
          <div className="bg-slate-50 p-2 rounded-lg text-center">
            <p className="text-slate-400 text-[10px]">SIZE</p>
            <p className="font-semibold text-slate-700">{doc.file_size_kb} KB</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 mt-5 pt-3 border-t border-slate-100">
        <button
          onClick={() => onChatWithDoc(doc.id)}
          className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-medium rounded-lg transition-colors"
        >
          <MessageSquare className="h-3.5 w-3.5" />
          <span>Chat</span>
        </button>

        <button
          onClick={() => onSummarizeDoc(doc.id)}
          className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-medium rounded-lg transition-colors"
        >
          <Sparkles className="h-3.5 w-3.5" />
          <span>Summary</span>
        </button>

        <button
          onClick={handleDelete}
          disabled={isDeleting}
          className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors disabled:opacity-50"
          title="Delete document and remove from FAISS"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

