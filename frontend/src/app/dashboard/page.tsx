"use client";

import { useState, useEffect } from 'react';
import { dashboardApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { LayoutDashboard, Award, FileText, AlertTriangle, ArrowRight, ShieldCheck, User, Bell, Clock, Download, Sparkles, CheckCircle2 } from 'lucide-react';

export default function CitizenDashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    dashboardApi.getStats()
      .then((data) => setStats(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col text-slate-100">
        <Navbar />
        <div className="flex-1 flex items-center justify-center flex-col p-4">
          <h2 className="text-xl font-bold">Please Log In</h2>
          <p className="text-xs text-slate-400 mt-1">Access your Citizen Welfare Dashboard</p>
          <Link href="/login" className="mt-4 px-4 py-2 bg-emerald-600 text-slate-950 rounded-xl text-xs font-bold">
            Log In Now
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-10">
        {/* Welcome Header Banner */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl mb-8 relative overflow-hidden flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-900/40">
              <User className="w-8 h-8" />
            </div>
            <div>
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">
                Citizen Welfare Dashboard
              </span>
              <h1 className="text-2xl lg:text-3xl font-extrabold text-white">
                Welcome, {stats.user_profile.full_name}!
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                District: <span className="text-white font-semibold">{stats.user_profile.district}</span> | Annual Income: <span className="text-white font-semibold">₹{stats.user_profile.annual_income.toLocaleString('en-IN')}</span>
              </p>
            </div>
          </div>

          <Link
            href="/assistant"
            className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-900/30 flex items-center gap-2 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Ask AI Welfare Officer</span>
          </Link>
        </div>

        {/* Missing Documents Alert Banner */}
        {stats.missing_documents && stats.missing_documents.length > 0 && (
          <div className="mb-8 p-4 rounded-2xl bg-amber-950/60 border border-amber-500/40 flex items-center justify-between flex-wrap gap-4 shadow-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-amber-300">
                  Missing Certificate Alert ({stats.missing_documents.length})
                </h4>
                <p className="text-xs text-slate-300">
                  Required docs still needed: <span className="font-semibold text-white">{stats.missing_documents.join(', ')}</span>
                </p>
              </div>
            </div>
            <span className="text-xs text-amber-400 font-semibold uppercase tracking-wider">
              Upload in Applications
            </span>
          </div>
        )}

        {/* Dashboard Metric Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-xl">
              {stats.eligible_schemes_count}
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-400">High Priority Schemes</span>
              <h3 className="text-lg font-extrabold text-white">Eligible Schemes</h3>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-teal-500/10 text-teal-400 flex items-center justify-center font-bold text-xl">
              {stats.applications.length}
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-400">Active Applications</span>
              <h3 className="text-lg font-extrabold text-white">In Progress</h3>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold text-xl">
              {stats.recent_queries.length}
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-400">AI Consultations</span>
              <h3 className="text-lg font-extrabold text-white">Recent Voice/Text</h3>
            </div>
          </div>
        </div>

        {/* Two Column Layout: Applications & Eligible Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
          {/* Applications List */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <span>My Welfare Applications</span>
              </h3>
              <Link href="/schemes" className="text-xs text-emerald-400 font-semibold hover:underline">
                Apply New
              </Link>
            </div>

            {stats.applications.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">No active applications yet. Browse schemes to start.</p>
            ) : (
              <div className="space-y-3">
                {stats.applications.map((app: any) => (
                  <div key={app.id} className="p-4 rounded-2xl bg-slate-900 border border-slate-850 flex items-center justify-between flex-wrap gap-2">
                    <div>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold text-[10px] uppercase">
                        {app.scheme_code}
                      </span>
                      <h4 className="text-xs font-bold text-white mt-1">{app.scheme_title}</h4>
                      <p className="text-[10px] text-slate-400">Status: {app.status}</p>
                    </div>

                    <Link
                      href={`/applications/${app.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-emerald-600 text-slate-200 hover:text-slate-950 font-bold text-xs flex items-center gap-1 transition-all"
                    >
                      <span>Journey</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Recommended High Priority Schemes */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 shadow-xl">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-400" />
              <span>AI Auto-Matched Schemes</span>
            </h3>

            <div className="space-y-3">
              {stats.high_priority_schemes.map((s: any) => (
                <div key={s.scheme_id} className="p-4 rounded-2xl bg-slate-900 border border-slate-850 flex items-center justify-between flex-wrap gap-2">
                  <div>
                    <span className="text-xs font-bold text-emerald-400">{s.code} ({s.eligibility_percentage}% Match)</span>
                    <h4 className="text-xs font-bold text-white">{s.title}</h4>
                  </div>
                  <Link
                    href={`/schemes/${s.scheme_id}`}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 text-slate-950 font-bold text-xs flex items-center gap-1 hover:bg-emerald-500 transition-colors"
                  >
                    <span>View</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
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
