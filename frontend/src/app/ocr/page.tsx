"use client";

import { useState } from 'react';
import { aiApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import { Cpu, Upload, FileText, Sparkles, BookOpen, Baby, Scale, ArrowRight } from 'lucide-react';

export default function OCRSimplifierPage() {
  const [legalText, setLegalText] = useState('');
  const [explanationLevel, setExplanationLevel] = useState<'simple' | 'eli10' | 'legal'>('simple');
  const [simplifiedResult, setSimplifiedResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSimplify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!legalText.trim()) return;
    setLoading(true);
    try {
      const res = await aiApi.askAssistant(legalText, explanationLevel);
      setSimplifiedResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 lg:px-8 py-10">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-3">
            <Cpu className="w-3.5 h-3.5" />
            <span>OCR & Legal Text Simplifier</span>
          </div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-white">
            Explain Like I'm 10 Legal Simplifier
          </h1>
          <p className="text-xs text-slate-400 mt-2">
            Paste complex government orders, legal jargon, or court notices to convert them instantly into simple language or child-friendly analogies.
          </p>
        </div>

        {/* Simplifier Box */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl mb-8">
          {/* Explanation mode toggle */}
          <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Input Legal Document Text</span>
            </h3>

            <div className="bg-slate-900 p-1.5 rounded-2xl border border-slate-800 flex items-center gap-1">
              <button
                type="button"
                onClick={() => setExplanationLevel('simple')}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  explanationLevel === 'simple' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                Simple
              </button>
              <button
                type="button"
                onClick={() => setExplanationLevel('eli10')}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  explanationLevel === 'eli10' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
                }`}
              >
                Explain Like I'm 10
              </button>
            </div>
          </div>

          <form onSubmit={handleSimplify} className="space-y-4">
            <textarea
              rows={6}
              value={legalText}
              onChange={(e) => setLegalText(e.target.value)}
              placeholder="Paste G.O. text e.g. 'Under G.O. MS No. 46/2023, Credit Linked Subsidy Scheme provisions apply to income ceiling Rs. 2,50,000...'"
              className="w-full p-4 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 shadow-inner"
            ></textarea>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading || !legalText.trim()}
                className="px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-900/30 flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Simplify Legal Document</span>
                    <Sparkles className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Simplification Result Display */}
          {simplifiedResult && (
            <div className="mt-8 p-6 rounded-2xl bg-slate-900/90 border border-cyan-500/30 shadow-xl space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                <span>Simplified AI Output ({explanationLevel.toUpperCase()} Mode)</span>
              </h4>

              <p className="text-sm text-slate-200 leading-relaxed text-justify whitespace-pre-line">
                {simplifiedResult.response}
              </p>

              <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                <span>AI Confidence: {(simplifiedResult.confidence_score * 100).toFixed(0)}%</span>
                <span>Sources Consulted: {simplifiedResult.sources?.length || 1}</span>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
