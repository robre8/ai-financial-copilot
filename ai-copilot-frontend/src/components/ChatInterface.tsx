import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../auth/AuthContext';

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
  const { token, user, signOut } = useAuth();
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

    if (!token) {
      setUploadMessage('❌ Inicia sesion para subir archivos');
      setTimeout(() => setUploadMessage(null), 3000);
      return;
    }
    
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
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
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
    if (!token) return;

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
      const response = await axios.post(
        `${API_BASE}/ask`,
        {
          question: tempQuestion,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-indigo-950">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-800/80 backdrop-blur-lg border-b border-slate-200/50 dark:border-slate-700/50 shadow-sm">
          <div className="max-w-6xl mx-auto px-4 py-5 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">💼</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
                  AI Financial Copilot
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Lightning-fast AI insights • Powered by Groq
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {user?.email && (
                <span className="text-xs font-medium text-slate-600 dark:text-slate-300 px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full">{user.email}</span>
              )}
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition text-lg"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              <button
                onClick={async () => {
                  await signOut();
                }}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 hover:bg-red-500/20 dark:hover:bg-red-500/30 transition border border-red-200 dark:border-red-800"
                title="Sign out"
              >
                Logout
              </button>
            </div>
          </div>
        </header>

        {/* Chat Container */}
        <main className="max-w-4xl mx-auto px-4 py-8">
          {/* Welcome Screen */}
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="mb-8 inline-block">
                <div className="relative inline-block">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl blur-2xl opacity-20"></div>
                  <div className="relative p-6 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-3xl">
                    <span className="text-6xl">📊</span>
                  </div>
                </div>
              </div>
              <h2 className="text-4xl font-bold text-slate-900 dark:text-white mb-4 bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
                Your AI Financial Advisor
              </h2>
              <p className="text-slate-600 dark:text-slate-400 text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
                Upload financial documents and get instant AI-powered analysis with Groq's industry-leading LLM technology.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-4xl mx-auto mb-8">
                <div className="p-5 bg-white dark:bg-slate-800/80 rounded-xl border border-blue-200 dark:border-blue-800 hover:shadow-lg hover:border-blue-400 dark:hover:border-blue-600 transition-all">
                  <p className="font-bold text-slate-900 dark:text-white mb-2 text-lg">📄 Upload PDF</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Upload any financial report, statement, or document</p>
                </div>
                <div className="p-5 bg-white dark:bg-slate-800/80 rounded-xl border border-purple-200 dark:border-purple-800 hover:shadow-lg hover:border-purple-400 dark:hover:border-purple-600 transition-all">
                  <p className="font-bold text-slate-900 dark:text-white mb-2 text-lg">✨ Ask Questions</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Query in natural language for instant insights</p>
                </div>
                <div className="p-5 bg-white dark:bg-slate-800/80 rounded-xl border border-pink-200 dark:border-pink-800 hover:shadow-lg hover:border-pink-400 dark:hover:border-pink-600 transition-all">
                  <p className="font-bold text-slate-900 dark:text-white mb-2 text-lg">⚡ Get Answers</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400">Receive AI analysis powered by Groq</p>
                </div>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-500">💡 Start by clicking the upload button or typing a question</p>
            </div>
          )}

          {/* Messages */}
          <div className="space-y-4 pb-96">
            {messages.map((msg) => (
              <div key={msg.id} className="animate-fadeIn">
                {/* User Question */}
                <div className="flex justify-end mb-3">
                  <div className="max-w-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl rounded-tr-none px-5 py-3 shadow-lg hover:shadow-xl transition-shadow">
                    <p className="text-sm font-medium">{msg.question}</p>
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
                      <div className="bg-red-50 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-2xl rounded-tl-none px-5 py-4 shadow-md">
                        <p className="text-sm text-red-700 dark:text-red-300 font-semibold">⚠️ Error occurred</p>
                        <p className="text-sm text-red-600 dark:text-red-300 mt-1">{msg.error}</p>
                      </div>
                    ) : (
                      <>
                        <div className="bg-white dark:bg-slate-800 rounded-2xl rounded-tl-none px-5 py-4 shadow-lg mb-3 border border-slate-200 dark:border-slate-700">
                          <p className="text-slate-900 dark:text-white text-sm leading-relaxed whitespace-pre-wrap font-medium">
                            {msg.answer}
                          </p>
                          
                          {/* Model & Chunks Info */}
                          <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700 flex flex-wrap items-center gap-2">
                            <span className={`text-xs text-white px-3 py-1 rounded-full font-bold ${getModelBadgeColor(msg.model)} shadow-md`}>
                              {msg.model === 'fallback-context' ? '⚡ Fallback' : msg.model}
                            </span>
                            <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-3 py-1 rounded-full font-semibold">
                              📌 {msg.chunkCount} chunk{msg.chunkCount !== 1 ? 's' : ''}
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
                              <div className="mt-3 bg-slate-50 dark:bg-slate-800/80 rounded-lg p-4 space-y-3 border border-slate-200 dark:border-slate-700">
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
          <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-slate-100/90 dark:from-slate-950/90 via-white/80 dark:via-slate-900/80 to-transparent pt-8 px-4 pb-6 backdrop-blur-sm">
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
                  className="px-5 py-3 bg-gradient-to-r from-indigo-500 to-blue-500 text-white font-semibold rounded-full hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  title="Upload PDF"
                >
                  {uploading ? '⏳' : '📁'}
                </button>

                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask anything about your documents..."
                  className="flex-1 px-5 py-3 rounded-full border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-500 dark:placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
                />
                <button
                  type="submit"
                  disabled={loading || !question.trim()}
                  className="px-7 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-full hover:shadow-xl hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg text-lg"
                >
                  {loading ? '⏳' : '✨'}
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
