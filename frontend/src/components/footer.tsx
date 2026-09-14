import { Shield, Heart, Globe, Lock } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 py-10 px-4 lg:px-8 text-slate-400 text-xs mt-20">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-5 h-5 text-emerald-400" />
            <span className="text-base font-bold text-white">JanSeva AI</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Offline-first Multilingual Legal Welfare Assistant empowering citizens with transparent access to official Indian government schemes.
          </p>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Features</h4>
          <ul className="space-y-2">
            <li><a href="/assistant" className="hover:text-emerald-400 transition-colors">Multilingual Voice AI Assistant</a></li>
            <li><a href="/eligibility" className="hover:text-emerald-400 transition-colors">Interactive Eligibility Meter</a></li>
            <li><a href="/schemes" className="hover:text-emerald-400 transition-colors">Scheme Alias Intelligence Engine</a></li>
            <li><a href="/ocr" className="hover:text-emerald-400 transition-colors">ELI10 Legal Document Simplifier</a></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Welfare Schemes</h4>
          <ul className="space-y-2">
            <li>Pradhan Mantri Awas Yojana (PMAY)</li>
            <li>PM-KISAN Samman Nidhi</li>
            <li>Kalaignar Magalir Urimai Thogai</li>
            <li>Ayushman Bharat Health Scheme</li>
            <li>Post-Matric Education Scholarship</li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3">Offline & Security</h4>
          <p className="text-slate-400 leading-relaxed mb-3">
            Local vector database & local LLM integration ensure complete offline availability without external cloud data dependency.
          </p>
          <div className="flex items-center gap-2 text-emerald-400 font-medium">
            <Lock className="w-4 h-4" />
            <span>100% Offline Village Ready</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto border-t border-slate-850 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-slate-500">© 2026 JanSeva AI Welfare Platform. Built for Indian Citizens.</p>
        <div className="flex items-center gap-4 text-slate-500">
          <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" /> Tamil / English / Hindi</span>
          <span className="flex items-center gap-1"><Heart className="w-3.5 h-3.5 text-rose-500" /> Public Welfare Tech</span>
        </div>
      </div>
    </footer>
  );
}
