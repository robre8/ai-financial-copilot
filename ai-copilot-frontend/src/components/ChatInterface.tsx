import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface ChatMessage {
  id: string;
  question: string;
  answer: string;
  model: string;
  chunks: string[];
  context: string;
  chunkCount: number;
  timestamp: Date;
  loading?: boolean;
  error?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export default function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [expandedMessage, setExpandedMessage] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const isDark = localStorage.getItem('darkMode') === 'true';
    setDarkMode(isDark);
    if (isDark) document.documentElement.classList.add('dark');
  }, []);

  const toggleDarkMode = () => {
    const newDark = !darkMode;
    setDarkMode(newDark);
    localStorage.setItem('darkMode', String(newDark));
    if (newDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file) return;
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadMessage('❌ Solo se aceptan archivos PDF');
      setTimeout(() => setUploadMessage(null), 3000);
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setUploadMessage('❌ El archivo es demasiado grande (máx 50MB)');
      setTimeout(() => setUploadMessage(null), 3000);
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      await axios.post(`${API_BASE}/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadMessage(`✅ ${file.name} subido correctamente`);
      setTimeout(() => setUploadMessage(null), 5000);
      // Refresh messages to show new context
      setMessages([...messages]);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || error.message;
      setUploadMessage(`❌ Error: ${errorMsg}`);
      setTimeout(() => setUploadMessage(null), 5000);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const tempQuestion = question;
    setQuestion('');
    
    const messageId = Date.now().toString();
    const tempMessage: ChatMessage = {
      id: messageId,
      question: tempQuestion,
      answer: '',
      model: '',
      chunks: [],
      context: '',
      chunkCount: 0,
      timestamp: new Date(),
      loading: true,
    };

    setMessages(prev => [...prev, tempMessage]);

    try {
      const response = await axios.post(`${API_BASE}/ask`, {
        question: tempQuestion,
      });

      const data = response.data;
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? {
                ...msg,
                answer: data.answer,
                model: data.model || 'unknown',
                chunks: data.chunks || [],
                context: data.context || '',
                chunkCount: data.chunk_count || 0,
                loading: false,
              }
            : msg
        )
      );
    } catch (error) {
      const errorMessage = axios.isAxiosError(error)
        ? error.response?.data?.detail || error.message
        : 'Failed to get response';

      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? {
                ...msg,
                error: errorMessage,
                loading: false,
              }
            : msg
        )
      );
    }
  };

  const getModelBadgeColor = (model: string) => {
    if (model.includes('70b')) return 'bg-gradient-to-r from-purple-500 to-pink-500';
    if (model.includes('8b-instant')) return 'bg-gradient-to-r from-blue-500 to-cyan-500';
    if (model.includes('mixtral')) return 'bg-gradient-to-r from-green-500 to-emerald-500';
    if (model === 'fallback-context') return 'bg-gray-500';
    return 'bg-gray-400';
  };

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950 dark:to-emerald-900">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">📊</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  AI Financial Copilot
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Powered by Groq + Huggingface
                </p>
              </div>
            </div>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </header>

        {/* Chat Container */}
        <main className="max-w-4xl mx-auto px-4 py-8">
          {/* Welcome Screen */}
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="mb-6">
                <div className="inline-block p-4 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-2xl">
                  <span className="text-5xl">💡</span>
                </div>
              </div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
                Welcome to AI Financial Copilot
              </h2>
              <p className="text-slate-600 dark:text-slate-400 text-lg mb-8 max-w-2xl mx-auto">
                Upload a PDF with financial data, then ask questions and get AI-powered insights powered by Groq's lightning-fast LLM API.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left max-w-3xl mx-auto">
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg">
                  <p className="font-semibold text-slate-900 dark:text-white mb-2">📄 Upload PDF</p>
                  <p className="text-sm text-slate-600 dark:text-slate-300">Start by uploading financial documents</p>
                </div>
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg">
                  <p className="font-semibold text-slate-900 dark:text-white mb-2">❓ Ask Questions</p>
                  <p className="text-sm text-slate-600 dark:text-slate-300">Query your documents with natural language</p>
                </div>
                <div className="p-4 bg-white dark:bg-slate-700 rounded-lg">
                  <p className="font-semibold text-slate-900 dark:text-white mb-2">⚡ Get Answers</p>
                  <p className="text-sm text-slate-600 dark:text-slate-300">Receive AI-powered financial insights</p>
                </div>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="space-y-4 pb-96">
            {messages.map((msg) => (
              <div key={msg.id} className="animate-fadeIn">
                {/* User Question */}
                <div className="flex justify-end mb-3">
                  <div className="max-w-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl rounded-tr-none px-5 py-3 shadow-md">
                    <p className="text-sm">{msg.question}</p>
                  </div>
                </div>

                {/* AI Response */}
                <div className="flex justify-start">
                  <div className="max-w-2xl">
                    {msg.loading ? (
                      <div className="bg-white dark:bg-slate-700 rounded-2xl rounded-tl-none px-5 py-4 shadow-md">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    ) : msg.error ? (
                      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl rounded-tl-none px-5 py-4 shadow-md">
                        <p className="text-sm text-red-700 dark:text-red-200 font-medium">⚠️ Error</p>
                        <p className="text-sm text-red-600 dark:text-red-300 mt-1">{msg.error}</p>
                      </div>
                    ) : (
                      <>
                        <div className="bg-white dark:bg-slate-700 rounded-2xl rounded-tl-none px-5 py-4 shadow-md mb-3">
                          <p className="text-slate-900 dark:text-white text-sm leading-relaxed whitespace-pre-wrap">
                            {msg.answer}
                          </p>
                          
                          {/* Model & Chunks Info */}
                          <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-600 flex flex-wrap items-center gap-2">
                            <span className={`text-xs text-white px-3 py-1 rounded-full font-semibold ${getModelBadgeColor(msg.model)} shadow-sm`}>
                              {msg.model === 'fallback-context' ? 'Fallback' : msg.model}
                            </span>
                            <span className="text-xs bg-slate-100 dark:bg-slate-600 text-slate-700 dark:text-slate-300 px-3 py-1 rounded-full">
                              {msg.chunkCount} chunk{msg.chunkCount !== 1 ? 's' : ''} retrieved
                            </span>
                          </div>
                        </div>

                        {/* Expandable Context */}
                        {(msg.chunks.length > 0 || msg.context) && (
                          <div className="mt-2">
                            <button
                              onClick={() => {
                                setExpandedMessage(expandedMessage === msg.id ? null : msg.id);
                                if (expandedMessage !== msg.id) {
                                  setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
                                }
                              }}
                              className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                            >
                              {expandedMessage === msg.id ? '▼' : '▶'} Show context & details
                            </button>
                            {expandedMessage === msg.id && (
                              <div className="mt-3 bg-slate-50 dark:bg-slate-800 rounded-lg p-4 space-y-3 border border-slate-200 dark:border-slate-600">
                                {msg.chunks.length > 0 && (
                                  <div>
                                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wide">
                                      Retrieved Chunks ({msg.chunks.length})
                                    </p>
                                    <div className="space-y-2">
                                      {msg.chunks.map((chunk, idx) => (
                                        <div key={idx} className="bg-white dark:bg-slate-700 p-3 rounded border border-slate-200 dark:border-slate-600">
                                          <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                                            <span className="font-semibold text-slate-600 dark:text-slate-400">Chunk {idx + 1}:</span> {chunk.substring(0, 200)}...
                                          </p>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                {msg.context && (
                                  <div>
                                    <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wide">
                                      Full Context Used
                                    </p>
                                    <div className="bg-white dark:bg-slate-700 p-3 rounded border border-slate-200 dark:border-slate-600">
                                      <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                                        {msg.context.substring(0, 500)}...
                                      </p>
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-slate-100 dark:from-slate-800 via-white dark:via-slate-800 to-transparent pt-8 px-4 pb-6">
            <div className="max-w-4xl mx-auto">
              {/* Upload Message */}
              {uploadMessage && (
                <div className={`mb-3 p-3 rounded-lg text-center text-sm font-medium ${
                  uploadMessage.includes('✅') 
                    ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200' 
                    : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200'
                }`}>
                  {uploadMessage}
                </div>
              )}
              
              <form onSubmit={handleAsk} className="flex gap-3">
                {/* Hidden File Input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleFileUpload(file);
                  }}
                  className="hidden"
                />
                
                {/* Upload Button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading || loading}
                  className="px-5 py-3 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-full hover:bg-slate-300 dark:hover:bg-slate-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Upload PDF"
                >
                  {uploading ? '⏳' : '📁'}
                </button>

                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask anything about your financial documents..."
                  className="flex-1 px-5 py-3 rounded-full border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={loading || !question.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-full hover:shadow-lg hover:scale-105 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? '⏳' : '📤'}
                </button>
              </form>
              <p className="text-xs text-slate-500 dark:text-slate-400 text-center mt-3">
                {messages.length} question{messages.length !== 1 ? 's' : ''} asked • Powered by Groq
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
