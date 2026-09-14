"use client";

import { useState } from 'react';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Shield, Sparkles, Mic, Search, CheckCircle2, AlertTriangle, ArrowRight, Home, Sprout, Heart, Activity, GraduationCap, Lock, FileText } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/schemes?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  const categories = [
    { icon: Home, title: 'Housing & Urban', count: 'PMAY-U, PMAY-G', color: 'from-emerald-600 to-teal-500' },
    { icon: Sprout, title: 'Agriculture & Farmers', count: 'PM-KISAN, Fertilizer Grants', color: 'from-green-600 to-emerald-500' },
    { icon: Heart, title: 'Women & Welfare', count: 'Magalir Urimai (KMT)', color: 'from-rose-600 to-pink-500' },
    { icon: Activity, title: 'Healthcare & Insurance', count: 'Ayushman Bharat (PM-JAY)', color: 'from-cyan-600 to-blue-500' },
    { icon: GraduationCap, title: 'Education & Youth', count: 'Pudhumai Penn, Post-Matric', color: 'from-amber-600 to-yellow-500' },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-16 lg:py-24 px-4 lg:px-8 max-w-7xl mx-auto text-center overflow-hidden">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold mb-6">
            <Sparkles className="w-4 h-4" />
            <span>100% Offline-First Multilingual AI Legal Welfare Platform</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight max-w-4xl mx-auto">
            Empowering Indian Citizens with <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-amber-300 bg-clip-text text-transparent">AI Welfare Intelligence</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto mt-6 leading-relaxed">
            Instant eligibility calculation, multi-language scheme alias matching (Tamil, English, Hindi), legal document simplification (ELI10), and automated government form filling.
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearchSubmit} className="mt-10 max-w-2xl mx-auto relative flex items-center">
            <Search className="w-5 h-5 text-slate-500 absolute left-4" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search scheme alias e.g. 'வீடு கட்ட உதவி', 'PMAY', 'Magalir Urimai', '6000 Rs Farmer'"
              className="w-full pl-12 pr-36 py-4 rounded-2xl bg-slate-900 border border-slate-800 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 shadow-2xl transition-all"
            />
            <button
              type="submit"
              className="absolute right-2 px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg transition-all"
            >
              Search Scheme
            </button>
          </form>

          {/* Primary Call-to-Actions */}
          <div className="mt-10 flex items-center justify-center gap-4 flex-wrap">
            <Link
              href="/assistant"
              className="px-6 py-3.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-xl shadow-emerald-900/40 flex items-center gap-2 transition-all"
            >
              <Mic className="w-4 h-4" />
              <span>Talk to Multilingual Voice AI Officer</span>
            </Link>

            <Link
              href="/eligibility"
              className="px-6 py-3.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 font-bold text-xs flex items-center gap-2 transition-all"
            >
              <CheckCircle2 className="w-4 h-4 text-amber-400" />
              <span>Interactive Eligibility Meter</span>
            </Link>
          </div>
        </section>

        {/* Live Scam Alert Banner */}
        <section className="max-w-7xl mx-auto px-4 lg:px-8 mb-16">
          <div className="p-6 rounded-3xl bg-gradient-to-r from-rose-950/80 via-slate-900 to-slate-950 border border-rose-500/30 flex items-center justify-between flex-wrap gap-4 shadow-2xl">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold flex-shrink-0">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-rose-300">
                  Government Advisory: Scheme Applications are 100% FREE
                </h3>
                <p className="text-xs text-slate-300 mt-0.5">
                  Beware of fake agents demanding money or commissions for PMAY, PM-KISAN, or Magalir Urimai approval. Report to Tamil Nadu Helpline 1100.
                </p>
              </div>
            </div>
            <span className="px-4 py-2 rounded-xl bg-rose-500/20 text-rose-300 font-bold text-xs border border-rose-500/30">
              Helpline: 1100
            </span>
          </div>
        </section>

        {/* Scheme Categories Grid */}
        <section className="max-w-7xl mx-auto px-4 lg:px-8 mb-20">
          <div className="text-center mb-12">
            <h2 className="text-2xl lg:text-3xl font-extrabold text-white">Browse Schemes by Domain</h2>
            <p className="text-xs text-slate-400 mt-1">Explore official central and state government welfare initiatives</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {categories.map((cat, idx) => {
              const IconComp = cat.icon;
              return (
                <Link
                  key={idx}
                  href="/schemes"
                  className="glass-panel p-6 rounded-2xl border border-slate-800 hover:border-emerald-500/40 transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${cat.color} flex items-center justify-center text-slate-950 shadow-md mb-4 group-hover:scale-105 transition-transform`}>
                      <IconComp className="w-6 h-6" />
                    </div>
                    <h3 className="text-sm font-bold text-white group-hover:text-emerald-400 transition-colors">{cat.title}</h3>
                    <p className="text-[11px] text-slate-400 mt-1">{cat.count}</p>
                  </div>
                  <div className="mt-6 flex items-center justify-end text-emerald-400">
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* Feature Highlights Grid */}
        <section className="max-w-7xl mx-auto px-4 lg:px-8 mb-20">
          <div className="glass-panel p-10 rounded-3xl border border-slate-800 shadow-2xl grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-3">
                <Mic className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">Multilingual Voice Interaction</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Speak directly in Tamil, English, or Hindi to search schemes and listen to speech responses.
              </p>
            </div>

            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-3">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">Explain Like I'm 10 (ELI10)</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Toggle between official legal summary, plain language, and child-friendly analogies for every scheme.
              </p>
            </div>

            <div>
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center mb-3">
                <Lock className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white mb-2">Offline Village Ready</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Runs locally with local vector database and local LLMs without requiring external cloud internet connection.
              </p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
