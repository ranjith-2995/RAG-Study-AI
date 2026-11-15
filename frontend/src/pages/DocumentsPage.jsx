import React, { useState } from 'react';
import { FileText, Search, UploadCloud, BookOpen } from 'lucide-react';
import DocumentCard from '../components/DocumentCard';
import FileUpload from '../components/FileUpload';

export default function DocumentsPage({ 
  documents, 
  onRefresh, 
  onChatWithDoc, 
  onSummarizeDoc, 
  onDeleteDocument 
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);

  const filteredDocs = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-800">Study Materials Library</h3>
          <p className="text-xs text-slate-500">
            View, manage, and delete uploaded PDF documents. Deleting a document removes its embeddings from FAISS.
          </p>
        </div>

        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-sm transition-all shrink-0"
        >
          <UploadCloud className="h-4 w-4" />
          <span>{showUpload ? 'Hide Upload Form' : 'Upload New PDF'}</span>
        </button>
      </div>

      {/* Upload Drawer (Conditional) */}
      {showUpload && (
        <div className="max-w-2xl">
          <FileUpload
            onUploadSuccess={() => {
              onRefresh();
              setShowUpload(false);
            }}
            onClose={() => setShowUpload(false)}
          />
        </div>
      )}

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="h-4 w-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search study documents by name..."
          className="w-full pl-10 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
        />
      </div>

      {/* Document Cards Grid */}
      {filteredDocs.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
          <div className="h-12 w-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
            <BookOpen className="h-6 w-6" />
          </div>
          <h4 className="text-sm font-semibold text-slate-700">No documents match your query</h4>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {searchQuery
              ? `No document found containing "${searchQuery}".`
              : "You haven't uploaded any PDF notes yet."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredDocs.map((doc) => (
            <DocumentCard
              key={doc.id}
              doc={doc}
              onChatWithDoc={onChatWithDoc}
              onSummarizeDoc={onSummarizeDoc}
              onDeleteDoc={onDeleteDocument}
            />
          ))}
        </div>
      )}
    </div>
  );
}

