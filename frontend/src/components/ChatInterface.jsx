import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Send, 
  Bot, 
  User, 
  Trash2, 
  FileText, 
  BookOpen, 
  ChevronDown, 
  ChevronUp, 
  Copy, 
  Check, 
  Loader2, 
  AlertCircle,
  HelpCircle,
  Sparkles
} from 'lucide-react';
import api from '../services/api';

export default function ChatInterface({ documents, selectedDocId, onSelectDocId }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "👋 Hello! I'm **STUDY MATE AI**, your intelligent study notes assistant. Upload your PDF notes or textbook chapters, and ask me any questions. I'll provide accurate answers retrieved directly from your study documents, complete with page citations!",
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (questionText = inputQuery) => {
    const q = questionText.trim();
    if (!q || loading) return;

    const userMsg = {
      id: String(Date.now()),
      role: 'user',
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const response = await api.askQuestion(q, selectedDocId);
      
      const assistantMsg = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: response.answer,
        sources: response.sources || [],
        found_in_docs: response.found_in_docs,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = {
        id: String(Date.now() + 1),
        role: 'assistant',
        content: `⚠️ **Error retrieving answer:** ${err.response?.data?.detail || err.message || 'Something went wrong. Please check your backend connection.'}`,
        sources: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Clear all messages in this study session?')) {
      setMessages([
        {
          id: 'welcome-reset',
          role: 'assistant',
          content: "Chat history cleared. What would you like to review next from your study materials?",
          sources: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleSourceExpand = (msgId) => {
    setExpandedSources((prev) => ({
      ...prev,
      [msgId]: !prev[msgId]
    }));
  };

  const starterPrompts = [
    "What are the main concepts and definitions?",
    "Summarize the key formulas or theories discussed.",
    "Explain the most important takeaway for exams.",
    "List the major steps or methods mentioned."
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Top Bar / Document Scope Selector */}
      <div className="px-6 py-3.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-blue-600" />
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Search Scope:</span>
          <select
            value={selectedDocId || ''}
            onChange={(e) => onSelectDocId(e.target.value || null)}
            className="text-xs bg-white border border-slate-300 rounded-lg px-3 py-1.5 font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 max-w-xs truncate"
          >
            <option value="">All Uploaded Documents ({documents.length})</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename} ({doc.total_pages} pages)
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleClearChat}
          className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-rose-600 hover:bg-rose-50 px-2.5 py-1.5 rounded-lg transition-colors"
          title="Clear chat history"
        >
          <Trash2 className="h-3.5 w-3.5" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          const hasSources = msg.sources && msg.sources.length > 0;
          const isSourceOpen = expandedSources[msg.id];

          return (
            <div
              key={msg.id}
              className={`flex gap-3.5 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              {/* Avatar */}
              <div
                className={`h-8 w-8 rounded-xl flex items-center justify-center shrink-0 text-white ${
                  isUser ? 'bg-blue-600' : 'bg-slate-800'
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              {/* Message Bubble */}
              <div className="space-y-2 max-w-2xl">
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed ${
                    isUser
                      ? 'bg-blue-600 text-white rounded-tr-none'
                      : 'bg-slate-100/80 text-slate-800 border border-slate-200/80 rounded-tl-none'
                  }`}
                >
                  {isUser ? (
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  ) : (
                    <div className="prose prose-sm max-w-none prose-slate prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-headings:font-semibold">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}

                  <div className={`flex items-center justify-between mt-2 pt-2 text-[10px] ${
                    isUser ? 'text-blue-200 border-t border-blue-500/40' : 'text-slate-400 border-t border-slate-200'
                  }`}>
                    <span>{msg.timestamp}</span>
                    {!isUser && (
                      <button
                        onClick={() => copyToClipboard(msg.content, msg.id)}
                        className="hover:text-slate-600 flex items-center gap-1 transition-colors"
                        title="Copy answer"
                      >
                        {copiedId === msg.id ? (
                          <>
                            <Check className="h-3 w-3 text-emerald-600" />
                            <span className="text-emerald-600 font-medium">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {/* Sources & Citations Accordion */}
                {hasSources && (
                  <div className="bg-slate-50 border border-slate-200 rounded-xl overflow-hidden text-xs">
                    <button
                      onClick={() => toggleSourceExpand(msg.id)}
                      className="w-full px-3.5 py-2 flex items-center justify-between text-slate-600 hover:bg-slate-100 font-medium transition-colors"
                    >
                      <span className="flex items-center gap-2">
                        <FileText className="h-3.5 w-3.5 text-blue-600" />
                        <span>Sources Referenced ({msg.sources.length} document excerpts)</span>
                      </span>
                      {isSourceOpen ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                    </button>

                    {isSourceOpen && (
                      <div className="p-3 space-y-2 border-t border-slate-200 bg-white">
                        {msg.sources.map((src, idx) => (
                          <div key={idx} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-700 mb-1">
                              <span className="flex items-center gap-1.5 text-blue-700 truncate max-w-xs">
                                <BookOpen className="h-3 w-3 shrink-0" />
                                {src.filename}
                              </span>
                              <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 font-mono text-[10px]">
                                Page {src.page}
                              </span>
                            </div>
                            <p className="text-slate-600 italic font-serif text-[11px] leading-relaxed bg-white p-2 rounded border border-slate-100">
                              "{src.snippet}"
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Loading Spinner */}
        {loading && (
          <div className="flex gap-3.5 mr-auto">
            <div className="h-8 w-8 rounded-xl bg-slate-800 text-white flex items-center justify-center">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-slate-100 border border-slate-200 rounded-2xl rounded-tl-none p-4 flex items-center gap-3 text-sm text-slate-600">
              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
              <span>Retrieving relevant chunks & synthesizing answer...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Starter Prompts (if chat is fresh) */}
      {messages.length <= 2 && !loading && (
        <div className="px-6 py-2 bg-slate-50/50 border-t border-slate-100">
          <p className="text-[11px] text-slate-400 font-medium mb-1.5">Quick Study Questions:</p>
          <div className="flex flex-wrap gap-2">
            {starterPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSend(prompt)}
                className="text-xs bg-white hover:bg-blue-50 hover:text-blue-700 text-slate-600 border border-slate-200 px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
              >
                <Sparkles className="h-3 w-3 text-blue-500" />
                <span>{prompt}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-200">
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 rounded-xl px-4 py-2 transition-all">
          <textarea
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              documents.length === 0
                ? "Please upload a PDF document first..."
                : "Ask anything about your study materials (Press Enter to send)..."
            }
            rows={1}
            disabled={loading}
            className="flex-1 bg-transparent border-none text-sm text-slate-800 placeholder-slate-400 focus:outline-none resize-none max-h-32"
          />
          <button
            onClick={() => handleSend()}
            disabled={!inputQuery.trim() || loading}
            className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg transition-colors shrink-0 shadow-sm shadow-blue-500/20"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
        <p className="text-[11px] text-slate-400 text-center mt-2">
          Study Mate AI strictly grounds answers on your uploaded PDFs to avoid hallucinations.
        </p>
      </div>
    </div>
  );
}

