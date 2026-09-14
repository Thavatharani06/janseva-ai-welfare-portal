"use client";

import { useState, useEffect } from 'react';
import { aiApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import { useAuth } from '@/lib/auth-context';
import { Mic, MicOff, Send, Sparkles, AlertTriangle, ShieldCheck, FileText, CheckCircle2, RefreshCw, Volume2, User, Bot, Scale, BookOpen, Baby } from 'lucide-react';

export default function AIAssistantPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<any[]>([]);
  const [inputText, setInputText] = useState('');
  const [explanationLevel, setExplanationLevel] = useState<'legal' | 'simple' | 'eli10'>('simple');
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Initial welcome message from AI Welfare Officer
    setMessages([
      {
        sender: 'ai',
        text: 'வணக்கம்! I am your JanSeva AI Legal Welfare Officer. How can I assist you with government schemes, housing grants, farmer subsidies, or legal document explanations today?',
        confidence: 0.98,
        sources: [],
        scam: null
      }
    ]);
  }, []);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    const userMsg = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setLoading(true);

    try {
      const data = await aiApi.askAssistant(query, explanationLevel);
      const aiMsg = {
        sender: 'ai',
        text: data.response,
        confidence: data.confidence_score,
        sources: data.sources || [],
        scam: data.scam_alert,
        matched_scheme: data.matched_scheme,
        reasoning: data.reasoning_summary
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err: any) {
      console.error(err);
      setMessages(prev => [...prev, {
        sender: 'ai',
        text: 'I apologize, but I encountered a network issue. Please ensure you are logged in or try again.',
        confidence: 0.50
      }]);
    } finally {
      setLoading(false);
    }
  };

  const startVoiceRecording = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('Speech recognition is supported directly via microphone text input.');
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = user?.language_preference === 'ta' ? 'ta-IN' : 'en-IN';
    recognition.interimResults = false;

    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setIsRecording(false);
      handleSendMessage(transcript);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);

    recognition.start();
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 lg:px-8 py-8 flex flex-col">
        {/* Officer Header */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 mb-6 flex items-center justify-between flex-wrap gap-4 shadow-2xl">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-900/40">
              <Bot className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold text-white">JanSeva AI Officer</h1>
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
              </div>
              <p className="text-xs text-slate-400">Offline-First Multilingual Legal Welfare Assistant</p>
            </div>
          </div>

          {/* Explanation Mode Controls */}
          <div className="bg-slate-900 p-1.5 rounded-2xl border border-slate-800 flex items-center gap-1">
            <button
              onClick={() => setExplanationLevel('simple')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                explanationLevel === 'simple' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Simple
            </button>
            <button
              onClick={() => setExplanationLevel('eli10')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                explanationLevel === 'eli10' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              ELI10
            </button>
            <button
              onClick={() => setExplanationLevel('legal')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                explanationLevel === 'legal' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              Legal G.O.
            </button>
          </div>
        </div>

        {/* Chat History Box */}
        <div className="flex-1 min-h-[420px] max-h-[550px] overflow-y-auto space-y-6 p-4 rounded-3xl bg-slate-900/40 border border-slate-800 mb-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.sender === 'ai' && (
                <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="w-5 h-5" />
                </div>
              )}

              <div className={`max-w-2xl rounded-3xl p-5 ${
                msg.sender === 'user'
                  ? 'bg-emerald-600 text-slate-950 font-medium text-xs shadow-lg'
                  : 'glass-panel border border-slate-800 text-slate-200 text-xs shadow-xl'
              }`}>
                {/* Scam Alert Banner inside message */}
                {msg.scam && (
                  <div className="mb-4 p-3 rounded-2xl bg-rose-950/80 border border-rose-500/40 text-rose-300 text-xs">
                    <div className="flex items-center gap-2 font-bold text-rose-400 mb-1">
                      <AlertTriangle className="w-4 h-4" />
                      <span>{msg.scam.warning_title}</span>
                    </div>
                    <p className="text-[11px] leading-relaxed">{msg.scam.warning_message}</p>
                  </div>
                )}

                <p className="whitespace-pre-line leading-relaxed text-sm">{msg.text}</p>

                {/* AI Source Transparency Badge & Citations */}
                {msg.sender === 'ai' && (
                  <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2">
                    <div className="flex items-center justify-between gap-2 text-[10px] font-bold text-slate-400">
                      <span className="flex items-center gap-1 text-emerald-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        AI Confidence: {(msg.confidence * 100).toFixed(0)}%
                      </span>
                      {msg.matched_scheme && (
                        <span className="bg-emerald-500/10 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/20 uppercase">
                          Scheme: {msg.matched_scheme.code}
                        </span>
                      )}
                    </div>

                    {msg.sources && msg.sources.length > 0 && (
                      <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850 text-[10px] space-y-1">
                        <span className="font-bold text-slate-300 block mb-1">Retrieved Citations & G.O. References:</span>
                        {msg.sources.map((s: any, sIdx: number) => (
                          <div key={sIdx} className="flex justify-between text-slate-400 border-b border-slate-900 pb-1">
                            <span>📄 {s.document_name} ({s.go_number})</span>
                            <span className="text-emerald-400 font-mono">Similarity: {(s.similarity_score * 100).toFixed(0)}%</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {msg.sender === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 text-slate-300 flex items-center justify-center flex-shrink-0 mt-1">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 items-center text-xs text-slate-400">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <span>AI Officer is searching official government vector database...</span>
            </div>
          )}
        </div>

        {/* Input Bar with Voice & Microphone */}
        <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="relative flex items-center gap-3">
          <button
            type="button"
            onClick={startVoiceRecording}
            className={`p-3.5 rounded-2xl border transition-all ${
              isRecording
                ? 'bg-rose-600 text-white border-rose-400 animate-bounce shadow-lg shadow-rose-900/50'
                : 'bg-slate-900 text-emerald-400 border-slate-800 hover:bg-slate-800'
            }`}
            title="Click to speak in Tamil or English"
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask AI Officer in Tamil or English e.g. 'How to get housing grant?' or 'வீடு கட்ட உதவி'"
            className="flex-1 py-3.5 px-5 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 shadow-xl"
          />

          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="p-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold transition-all disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </main>

      <Footer />
    </div>
  );
}
