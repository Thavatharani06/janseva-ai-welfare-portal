"use client";

import { useState, useEffect } from 'react';
import { schemeApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import Link from 'next/link';
import { Search, Sparkles, FileText, ArrowRight, CheckCircle2, Languages, Building2, Tag, ShieldCheck } from 'lucide-react';

export default function SchemesCatalogPage() {
  const [schemes, setSchemes] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [selectedCat, setSelectedCat] = useState<string>('');
  const [search, setSearch] = useState<string>('');
  const [aliasSearchResult, setAliasSearchResult] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, [selectedCat]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [catData, schemeData] = await Promise.all([
        schemeApi.getCategories(),
        schemeApi.getAll(search, selectedCat)
      ]);
      setCategories(catData);
      setSchemes(schemeData);
    } catch (err) {
      console.error('Error loading scheme catalog:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!search.trim()) {
      setAliasSearchResult(null);
      loadData();
      return;
    }

    setLoading(true);
    try {
      const result = await schemeApi.searchByAlias(search);
      setAliasSearchResult(result);
      if (result.matched_scheme) {
        setSchemes([result.matched_scheme]);
      } else {
        const fallback = await schemeApi.getAll(search, selectedCat);
        setSchemes(fallback);
      }
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-10">
        {/* Header */}
        <div className="mb-10 text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Multilingual Scheme Alias Engine</span>
          </div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-white">
            Government Welfare Scheme Catalog
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            Search schemes in Tamil, English, or Hindi using localized names, acronyms, or nicknames (e.g. "வீடு கட்ட உதவி", "PMAY", "MAGALIR URIMAI").
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearchSubmit} className="mt-8 relative max-w-2xl mx-auto">
            <div className="relative flex items-center">
              <Search className="w-5 h-5 text-slate-500 absolute left-4" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by alias e.g. 'வீடு கட்ட உதவி' or 'PMAY' or '1000 Rs Scheme'"
                className="w-full pl-12 pr-32 py-3.5 rounded-2xl bg-slate-900 border border-slate-800 text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-xl transition-all"
              />
              <button
                type="submit"
                className="absolute right-2 px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-md transition-all"
              >
                Resolve Alias
              </button>
            </div>
          </form>
        </div>

        {/* Alias Match Highlight Banner */}
        {aliasSearchResult && aliasSearchResult.matched_scheme && (
          <div className="mb-8 p-4 rounded-2xl bg-gradient-to-r from-emerald-950/60 to-teal-950/60 border border-emerald-500/30 flex items-center justify-between flex-wrap gap-4 shadow-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm">
                {(aliasSearchResult.confidence * 100).toFixed(0)}%
              </div>
              <div>
                <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wide">
                  Alias Resolved to Code: {aliasSearchResult.matched_scheme.code}
                </span>
                <h4 className="text-base font-bold text-white">
                  {aliasSearchResult.matched_scheme.title} ({aliasSearchResult.matched_scheme.title_ta})
                </h4>
                <p className="text-xs text-slate-400">Matched Term: "{aliasSearchResult.matched_alias}"</p>
              </div>
            </div>
            <Link
              href={`/schemes/${aliasSearchResult.matched_scheme.id}`}
              className="px-4 py-2 rounded-xl bg-emerald-600 text-slate-950 font-bold text-xs flex items-center gap-2 hover:bg-emerald-500 transition-colors"
            >
              <span>View Scheme Details</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        )}

        {/* Category Filters */}
        <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-8">
          <button
            onClick={() => { setSelectedCat(''); setAliasSearchResult(null); setSearch(''); }}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
              selectedCat === '' ? 'bg-emerald-600 text-slate-950 shadow-md' : 'bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800'
            }`}
          >
            All Schemes
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => { setSelectedCat(cat.id); setAliasSearchResult(null); }}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap flex items-center gap-2 ${
                selectedCat === cat.id ? 'bg-emerald-600 text-slate-950 shadow-md' : 'bg-slate-900 text-slate-300 border border-slate-800 hover:bg-slate-800'
              }`}
            >
              <span>{cat.name}</span>
            </button>
          ))}
        </div>

        {/* Schemes Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-64 rounded-2xl bg-slate-900/60 animate-pulse border border-slate-800"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {schemes.map((scheme) => (
              <div key={scheme.id} className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between hover:border-emerald-500/40 transition-all group">
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-[10px] font-extrabold uppercase tracking-wider border border-emerald-500/20">
                      {scheme.code}
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">
                      {scheme.category?.name || 'Welfare'}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-white group-hover:text-emerald-300 transition-colors mb-1">
                    {scheme.title}
                  </h3>
                  {scheme.title_ta && (
                    <p className="text-xs font-semibold text-emerald-400 mb-3">
                      {scheme.title_ta}
                    </p>
                  )}

                  <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed mb-4">
                    {scheme.simple_summary}
                  </p>

                  {/* Aliases Pills */}
                  {scheme.aliases && scheme.aliases.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mb-6">
                      {scheme.aliases.slice(0, 3).map((a: any) => (
                        <span key={a.id} className="px-2 py-0.5 rounded bg-slate-850 text-slate-400 text-[10px] border border-slate-800">
                          {a.alias}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="pt-4 border-t border-slate-850 flex items-center justify-between">
                  <div className="text-[11px] text-slate-400">
                    Max Income: <span className="text-white font-semibold">{scheme.max_income ? `₹${scheme.max_income.toLocaleString('en-IN')}` : 'No limit'}</span>
                  </div>

                  <Link
                    href={`/schemes/${scheme.id}`}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-emerald-600 hover:text-slate-950 text-slate-200 text-xs font-bold transition-all flex items-center gap-1"
                  >
                    <span>View Scheme</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
