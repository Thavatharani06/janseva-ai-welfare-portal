"use client";

import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Shield, User as UserIcon, LogOut, Languages, Cpu, FileText, CheckCircle2, Mic, LayoutDashboard, Lock } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout, setLanguage } = useAuth();
  const [langMenu, setLangMenu] = useState(false);

  const languages = [
    { code: 'ta', label: 'தமிழ் (Tamil)' },
    { code: 'en', label: 'English' },
    { code: 'hi', label: 'हिन्दी (Hindi)' }
  ];

  return (
    <nav className="glass-panel sticky top-0 z-50 px-4 lg:px-8 py-3 flex items-center justify-between border-b border-slate-800">
      {/* Brand Logo */}
      <Link href="/" className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-emerald-400 flex items-center justify-center shadow-lg shadow-emerald-900/40 group-hover:scale-105 transition-transform">
          <Shield className="w-6 h-6 text-slate-950 font-bold" />
        </div>
        <div>
          <span className="text-xl font-extrabold bg-gradient-to-r from-emerald-400 via-teal-300 to-amber-300 bg-clip-text text-transparent">
            JanSeva AI
          </span>
          <span className="block text-[10px] uppercase tracking-widest text-emerald-400 font-semibold">
            Multilingual Welfare Assistant
          </span>
        </div>
      </Link>

      {/* Navigation Links */}
      <div className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
        <Link href="/assistant" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
          <Mic className="w-4 h-4 text-emerald-400" />
          AI Officer
        </Link>
        <Link href="/eligibility" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
          <CheckCircle2 className="w-4 h-4 text-amber-400" />
          Eligibility Meter
        </Link>
        <Link href="/schemes" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
          <FileText className="w-4 h-4 text-teal-400" />
          Scheme Alias Catalog
        </Link>
        <Link href="/ocr" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
          <Cpu className="w-4 h-4 text-cyan-400" />
          Legal Simplifier
        </Link>
        {user && (
          <Link href="/dashboard" className="flex items-center gap-2 hover:text-emerald-400 transition-colors">
            <LayoutDashboard className="w-4 h-4 text-emerald-300" />
            Dashboard
          </Link>
        )}
        {user?.role === 'admin' && (
          <Link href="/admin" className="flex items-center gap-2 text-amber-400 hover:text-amber-300 transition-colors font-semibold">
            <Lock className="w-4 h-4" />
            Admin Portal
          </Link>
        )}
      </div>

      {/* Action Buttons & Language selector */}
      <div className="flex items-center gap-4">
        {/* Language selector */}
        <div className="relative">
          <button 
            onClick={() => setLangMenu(!langMenu)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 transition-all"
          >
            <Languages className="w-3.5 h-3.5 text-emerald-400" />
            <span>{languages.find(l => l.code === (user?.language_preference || 'ta'))?.label.split(' ')[0]}</span>
          </button>

          {langMenu && (
            <div className="absolute right-0 mt-2 w-44 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl overflow-hidden py-1 z-50">
              {languages.map((l) => (
                <button
                  key={l.code}
                  onClick={() => {
                    setLanguage(l.code);
                    setLangMenu(false);
                  }}
                  className={`w-full text-left px-4 py-2 text-xs hover:bg-slate-800 transition-colors flex items-center justify-between ${
                    (user?.language_preference || 'ta') === l.code ? 'text-emerald-400 font-bold bg-slate-850' : 'text-slate-300'
                  }`}
                >
                  <span>{l.label}</span>
                  {(user?.language_preference || 'ta') === l.code && <span className="w-2 h-2 rounded-full bg-emerald-400"></span>}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User Auth Buttons */}
        {user ? (
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col text-right">
              <span className="text-xs font-bold text-slate-200">{user.full_name}</span>
              <span className="text-[10px] text-emerald-400 capitalize">{user.role} • {user.district || 'Tamil Nadu'}</span>
            </div>
            <button
              onClick={logout}
              title="Logout"
              className="p-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition-all"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition-colors"
            >
              Login
            </Link>
            <Link
              href="/register"
              className="px-4 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-slate-950 shadow-md shadow-emerald-900/30 transition-all"
            >
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
