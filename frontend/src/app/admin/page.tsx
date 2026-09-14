"use client";

import { useState, useEffect } from 'react';
import { dashboardApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import { Lock, Users, ShieldAlert, Cpu, Activity, BarChart3, Upload, FileText, CheckCircle2, Globe, Database } from 'lucide-react';

function MySchemeSyncController() {
  const [syncing, setSyncing] = useState(false);
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    setMetrics(null);
    setError(null);
    try {
      const res = await dashboardApi.triggerMySchemeSync();
      if (res.status === 'success') {
        setMetrics(res.metrics);
      } else {
        setError(res.message || 'Synchronization completed with errors.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to ingestion service.');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-3xl border border-slate-800 mb-8 bg-slate-900/50">
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-amber-500 animate-pulse" />
            <span>Update Government Schemes (myScheme Portal Sync)</span>
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Download latest scheme metadata, extract structured eligibility limits, auto-generate aliases, and rebuild the local RAG knowledge index.
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-600 text-slate-950 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {syncing ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
              <span>Syncing myScheme Database...</span>
            </>
          ) : (
            <>
              <Cpu className="w-4 h-4" />
              <span>Update Government Schemes</span>
            </>
          )}
        </button>
      </div>

      {metrics && (
        <div className="mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
          <div className="flex items-center gap-2 font-bold mb-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>Sync Complete Successfully!</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 mt-2 text-slate-350">
            <div>
              <span className="text-slate-400 block">Schemes Ingested</span>
              <strong className="text-white text-sm">{metrics.schemes_processed}</strong>
            </div>
            <div>
              <span className="text-slate-400 block">Categories Created</span>
              <strong className="text-white text-sm">{metrics.categories_created}</strong>
            </div>
            <div>
              <span className="text-slate-400 block">Eligibility Rules</span>
              <strong className="text-white text-sm">{metrics.rules_created}</strong>
            </div>
            <div>
              <span className="text-slate-400 block">Aliases Generated</span>
              <strong className="text-white text-sm">{metrics.aliases_created}</strong>
            </div>
            <div>
              <span className="text-slate-400 block">RAG Embeddings</span>
              <strong className="text-white text-sm">{metrics.rag_chunks_created}</strong>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

export default function AdminPortalPage() {

  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    dashboardApi.getAdminAnalytics()
      .then((data) => setAnalytics(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
        <Navbar />
        <div className="flex-1 flex items-center justify-center flex-col p-4">
          <Lock className="w-12 h-12 text-amber-500 mb-2" />
          <h2 className="text-xl font-bold">Admin Privilege Required</h2>
          <p className="text-xs text-slate-400 mt-1">Please log in as admin (admin@janseva.gov.in)</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-10">
        {/* Header */}
        <div className="glass-panel p-8 rounded-3xl border border-amber-500/30 shadow-2xl mb-8 flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold">
              <Lock className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-bold text-amber-400 uppercase tracking-widest">
                Government Welfare Admin Portal
              </span>
              <h1 className="text-2xl font-extrabold text-white">System Analytics & Ingestion Controller</h1>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
              Avg AI Confidence: {analytics.overview.average_ai_confidence}%
            </span>
          </div>
        </div>

        {/* myScheme Ingestion Engine Section */}
        <MySchemeSyncController />


        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400">Total Registered Citizens</span>
            <h3 className="text-2xl font-extrabold text-white mt-1">{analytics.overview.total_users}</h3>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400">Submitted Applications</span>
            <h3 className="text-2xl font-extrabold text-white mt-1">{analytics.overview.total_applications}</h3>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400">AI Consultations Handled</span>
            <h3 className="text-2xl font-extrabold text-white mt-1">{analytics.overview.total_ai_queries}</h3>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-rose-500/30">
            <span className="text-xs font-semibold text-rose-400">Scam Attempts Flagged</span>
            <h3 className="text-2xl font-extrabold text-rose-400 mt-1">{analytics.overview.scam_attempts_flagged}</h3>
          </div>
        </div>

        {/* Analytics Breakdown Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Popular Districts */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-emerald-400" />
              <span>District-Wise Citizen Activity</span>
            </h3>

            <div className="space-y-3">
              {analytics.popular_districts.map((d: any, idx: number) => (
                <div key={idx} className="flex justify-between items-center p-3 rounded-xl bg-slate-900 border border-slate-850 text-xs">
                  <span className="font-semibold text-white">{d.district}</span>
                  <span className="text-emerald-400 font-bold">{d.user_count} Citizens</span>
                </div>
              ))}
            </div>
          </div>

          {/* Popular Languages */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Globe className="w-4 h-4 text-amber-400" />
              <span>Language Usage Distribution</span>
            </h3>

            <div className="space-y-3">
              {analytics.popular_languages.map((l: any, idx: number) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold">
                    <span className="text-white">{l.language}</span>
                    <span className="text-amber-400">{l.percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
                    <div className="bg-amber-500 h-full rounded-full" style={{ width: `${l.percentage}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
