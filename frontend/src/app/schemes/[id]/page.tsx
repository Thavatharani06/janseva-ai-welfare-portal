"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { schemeApi, applicationApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Shield, Sparkles, FileText, CheckCircle2, AlertTriangle, ArrowLeft, ArrowRight, ExternalLink, Phone, Building, Baby, Scale, BookOpen } from 'lucide-react';

export default function SchemeDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [scheme, setScheme] = useState<any>(null);
  const [explanationLevel, setExplanationLevel] = useState<'legal' | 'simple' | 'eli10'>('simple');
  const [loading, setLoading] = useState<boolean>(true);
  const [creatingApp, setCreatingApp] = useState<boolean>(false);

  useEffect(() => {
    if (id) {
      schemeApi.getById(id as string)
        .then((data) => setScheme(data))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleStartApplication = async () => {
    if (!user) {
      window.location.href = '/login';
      return;
    }
    setCreatingApp(true);
    try {
      const app = await applicationApi.createApplication(scheme.id);
      window.location.href = `/applications/${app.id}`;
    } catch (err) {
      console.error(err);
    } finally {
      setCreatingApp(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!scheme) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
        <Navbar />
        <div className="flex-1 flex items-center justify-center flex-col p-4">
          <h2 className="text-xl font-bold">Scheme Not Found</h2>
          <Link href="/schemes" className="mt-4 px-4 py-2 bg-emerald-600 text-slate-950 rounded-xl text-xs font-bold">
            Back to Catalog
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 lg:px-8 py-10">
        <Link href="/schemes" className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white mb-6">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Schemes Catalog</span>
        </Link>

        {/* Scheme Title Header */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl mb-8 relative overflow-hidden">
          <div className="flex items-center justify-between gap-4 flex-wrap mb-4">
            <span className="px-3 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-extrabold uppercase tracking-wider border border-emerald-500/20">
              {scheme.code}
            </span>
            {scheme.helpline_number && (
              <span className="text-xs text-amber-400 font-semibold flex items-center gap-1.5 bg-amber-500/10 px-3 py-1 rounded-lg border border-amber-500/20">
                <Phone className="w-3.5 h-3.5" />
                Helpline: {scheme.helpline_number}
              </span>
            )}
          </div>

          <h1 className="text-3xl font-extrabold text-white mb-2">{scheme.title}</h1>
          {scheme.title_ta && <p className="text-base font-semibold text-emerald-400 mb-4">{scheme.title_ta}</p>}

          <p className="text-xs text-slate-400 flex items-center gap-2 mb-6">
            <Building className="w-4 h-4 text-slate-500" />
            <span>Ministry: {scheme.ministry || 'Government of India / State Government'}</span>
          </p>

          {/* Explanation Mode Toggle Buttons */}
          <div className="bg-slate-900/80 p-1.5 rounded-2xl border border-slate-800 flex items-center gap-2 max-w-md">
            <button
              onClick={() => setExplanationLevel('simple')}
              className={`flex-1 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                explanationLevel === 'simple' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Simple</span>
            </button>
            <button
              onClick={() => setExplanationLevel('eli10')}
              className={`flex-1 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                explanationLevel === 'eli10' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Baby className="w-3.5 h-3.5" />
              <span>Explain Like I'm 10</span>
            </button>
            <button
              onClick={() => setExplanationLevel('legal')}
              className={`flex-1 py-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                explanationLevel === 'legal' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Legal Summary</span>
            </button>
          </div>
        </div>

        {/* Dynamic Explanation Content Card */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-xl mb-8">
          <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4" />
            <span>
              {explanationLevel === 'simple' && 'Plain Language Summary'}
              {explanationLevel === 'eli10' && 'Child-Friendly Analogy (ELI10 Mode)'}
              {explanationLevel === 'legal' && 'Official Government Gazette & Legal Clauses'}
            </span>
          </h3>

          <p className="text-sm text-slate-200 leading-relaxed text-justify whitespace-pre-line">
            {explanationLevel === 'simple' && scheme.simple_summary}
            {explanationLevel === 'eli10' && scheme.eli10_summary}
            {explanationLevel === 'legal' && scheme.legal_summary}
          </p>
        </div>

        {/* Requirements & Action Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
          {/* Eligibility Specs */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Eligibility Parameters</span>
            </h4>
            <ul className="space-y-3 text-xs text-slate-300">
              <li className="flex justify-between border-b border-slate-850 pb-2">
                <span className="text-slate-400">Age Limit</span>
                <span className="font-semibold">{scheme.min_age} to {scheme.max_age} years</span>
              </li>
              <li className="flex justify-between border-b border-slate-850 pb-2">
                <span className="text-slate-400">Income Limit</span>
                <span className="font-semibold">{scheme.max_income ? `Up to ₹${scheme.max_income.toLocaleString('en-IN')}` : 'No ceiling'}</span>
              </li>
              <li className="flex justify-between border-b border-slate-850 pb-2">
                <span className="text-slate-400">Gender Restriction</span>
                <span className="font-semibold">{scheme.gender_restriction || 'All'}</span>
              </li>
              <li className="flex justify-between pb-1">
                <span className="text-slate-400">State / Scope</span>
                <span className="font-semibold">{scheme.state_district_scope || 'All India'}</span>
              </li>
            </ul>
          </div>

          {/* Required Documents */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4 text-amber-400" />
              <span>Required Application Documents</span>
            </h4>
            <ul className="space-y-2 text-xs text-slate-300">
              {(scheme.required_documents || []).map((doc: string, idx: number) => (
                <li key={idx} className="flex items-center gap-2 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span>{doc}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Start Application Action Bar */}
        <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-900/40 via-teal-900/40 to-slate-900 border border-emerald-500/30 flex items-center justify-between flex-wrap gap-4 shadow-2xl">
          <div>
            <h4 className="text-base font-bold text-white">Ready to apply for {scheme.code}?</h4>
            <p className="text-xs text-slate-300 mt-1">Our AI Assistant will detect missing documents and auto-fill your official application form.</p>
          </div>

          <button
            onClick={handleStartApplication}
            disabled={creatingApp}
            className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-900/40 flex items-center gap-2 transition-all"
          >
            {creatingApp ? (
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                <span>Start Guided Application</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </main>

      <Footer />
    </div>
  );
}
