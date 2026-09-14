"use client";

import { useState } from 'react';
import { eligibilityApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';
import { Sparkles, CheckCircle2, XCircle, ArrowRight, ShieldCheck, HeartHandshake, User, DollarSign, MapPin, Briefcase, Heart, Award, ArrowDownRight } from 'lucide-react';

export default function EligibilityMeterPage() {
  const { user } = useAuth();

  // Life Event prompt state
  const [lifeEventPrompt, setLifeEventPrompt] = useState('');
  const [lifeEventResult, setLifeEventResult] = useState<any>(null);
  const [lifeLoading, setLifeLoading] = useState(false);

  // Demographics form state
  const [formData, setFormData] = useState({
    age: user?.age || 32,
    gender: user?.gender || 'female',
    annual_income: user?.annual_income || 120000,
    district: user?.district || 'Madurai',
    occupation: user?.occupation || 'Unorganized Worker',
    disability_status: user?.disability_status || false,
    community: user?.community || 'OBC',
    marital_status: user?.marital_status || 'Married'
  });

  const [eligibilityResult, setEligibilityResult] = useState<any>(null);
  const [meterLoading, setMeterLoading] = useState(false);

  const handleLifeEventSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lifeEventPrompt.trim()) return;
    setLifeLoading(true);
    try {
      const res = await eligibilityApi.reasonLifeEvent(lifeEventPrompt);
      setLifeEventResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLifeLoading(false);
    }
  };

  const handleMeterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMeterLoading(true);
    try {
      const res = await eligibilityApi.checkEligibility(formData);
      setEligibilityResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setMeterLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-10">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Life Event & Welfare Recommendation Engine</span>
          </div>
          <h1 className="text-3xl lg:text-4xl font-extrabold text-white">
            Smart Eligibility Meter & Life Event Assistant
          </h1>
          <p className="text-xs text-slate-400 mt-2">
            Describe your life situation in plain language (e.g., "My daughter is joining college", "My husband passed away") or evaluate your 10-parameter demographic profile.
          </p>
        </div>

        {/* Section 1: Life Event Reasoning Engine */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl mb-12 relative overflow-hidden">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
              <HeartHandshake className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Life Event Assistant</h2>
              <p className="text-xs text-slate-400">Describe what changed in your life to discover tailored welfare support</p>
            </div>
          </div>

          <form onSubmit={handleLifeEventSubmit} className="flex gap-3 flex-wrap">
            <input
              type="text"
              value={lifeEventPrompt}
              onChange={(e) => setLifeEventPrompt(e.target.value)}
              placeholder="e.g. 'My husband passed away', 'My daughter is joining engineering', 'I lost my job'"
              className="flex-1 min-w-[280px] py-3.5 px-5 rounded-2xl bg-slate-900 border border-slate-800 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-amber-500 shadow-xl"
            />
            <button
              type="submit"
              disabled={lifeLoading}
              className="px-6 py-3.5 rounded-2xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-900/30 flex items-center gap-2 transition-all disabled:opacity-50"
            >
              {lifeLoading ? (
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <span>Analyze Life Situation</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick preset buttons */}
          <div className="flex flex-wrap gap-2 mt-4">
            <span className="text-[11px] text-slate-400 flex items-center">Quick Examples:</span>
            {[
              "My husband passed away",
              "My daughter is joining engineering",
              "I lost my job",
              "Need house construction subsidy"
            ].map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() => { setLifeEventPrompt(ex); handleLifeEventSubmit({ preventDefault: () => {} } as any); }}
                className="px-3 py-1 rounded-lg bg-slate-900 text-slate-300 text-[11px] border border-slate-800 hover:border-amber-500/40 transition-colors"
              >
                "{ex}"
              </button>
            ))}
          </div>

          {/* Life Event Results Display */}
          {lifeEventResult && (
            <div className="mt-6 p-6 rounded-2xl bg-slate-900/80 border border-amber-500/30">
              <div className="flex items-center justify-between mb-3">
                <span className="px-3 py-1 rounded-lg bg-amber-500/10 text-amber-400 text-xs font-bold uppercase border border-amber-500/20">
                  Detected Event: {lifeEventResult.event_title}
                </span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed mb-4">{lifeEventResult.guidance_advice}</p>

              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Recommended Welfare Schemes:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {lifeEventResult.recommended_schemes.map((s: any) => (
                  <div key={s.id} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-emerald-400">{s.code}</span>
                      <h5 className="text-xs font-semibold text-white">{s.title}</h5>
                    </div>
                    <Link href={`/schemes/${s.id}`} className="p-2 rounded-lg bg-slate-850 hover:bg-emerald-600 text-slate-300 hover:text-slate-950 transition-colors">
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Section 2: 10-Parameter Visual Eligibility Meter */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Questionnaire Form */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800 shadow-xl">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-emerald-400" />
              <span>Demographic Questionnaire</span>
            </h3>

            <form onSubmit={handleMeterSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Age (Years)</label>
                <input
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({ ...formData, age: Number(e.target.value) })}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Gender</label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Annual Household Income (₹)</label>
                <input
                  type="number"
                  value={formData.annual_income}
                  onChange={(e) => setFormData({ ...formData, annual_income: Number(e.target.value) })}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">District</label>
                <input
                  type="text"
                  value={formData.district}
                  onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Occupation</label>
                <select
                  value={formData.occupation}
                  onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Unorganized Worker">Unorganized Worker / Laborer</option>
                  <option value="Farmer">Farmer / Agriculture</option>
                  <option value="Student">Student</option>
                  <option value="Self Employed">Self Employed / Small Business</option>
                  <option value="Homemaker">Homemaker</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Community Category</label>
                <select
                  value={formData.community}
                  onChange={(e) => setFormData({ ...formData, community: e.target.value })}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="OBC">OBC / MBC</option>
                  <option value="SC">SC / ST</option>
                  <option value="General">General</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={meterLoading}
                className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-900/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 mt-4"
              >
                {meterLoading ? (
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Calculate Scheme Eligibility</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Meter Output & Ranked Scheme Cards */}
          <div className="lg:col-span-2 space-y-6">
            {!eligibilityResult ? (
              <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center flex flex-col items-center justify-center min-h-[400px]">
                <ShieldCheck className="w-16 h-16 text-emerald-500/40 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">Ready to Calculate Eligibility</h3>
                <p className="text-xs text-slate-400 max-w-md">
                  Click 'Calculate Scheme Eligibility' to see your personalized visual eligibility meter and ranked scheme priority breakdown.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* High Priority Schemes */}
                <div className="glass-panel p-6 rounded-3xl border border-emerald-500/40">
                  <h4 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Award className="w-5 h-5 text-emerald-400" />
                    <span>High Priority Matches ({eligibilityResult.recommendations.high_priority.length})</span>
                  </h4>

                  <div className="space-y-4">
                    {eligibilityResult.recommendations.high_priority.map((item: any) => (
                      <div key={item.scheme_id} className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3">
                        <div className="flex items-center justify-between flex-wrap gap-2">
                          <div>
                            <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-extrabold text-[10px] uppercase">
                              {item.code}
                            </span>
                            <h5 className="text-base font-bold text-white mt-1">{item.title}</h5>
                          </div>
                          {/* Meter Bar */}
                          <div className="flex items-center gap-3">
                            <div className="w-24 bg-slate-800 rounded-full h-3 overflow-hidden">
                              <div
                                className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500"
                                style={{ width: `${item.eligibility_percentage}%` }}
                              ></div>
                            </div>
                            <span className="text-xs font-extrabold text-emerald-400">{item.eligibility_percentage}%</span>
                          </div>
                        </div>

                        {/* Reasons for eligibility */}
                        <div className="bg-slate-950 p-3 rounded-xl border border-slate-850 text-[11px] space-y-1">
                          <span className="text-xs font-semibold text-emerald-400 block mb-1">✔ Reasons for Eligibility:</span>
                          {item.reasons_eligible.map((r: string, rIdx: number) => (
                            <p key={rIdx} className="text-slate-300">• {r}</p>
                          ))}
                        </div>

                        <div className="flex justify-end">
                          <Link href={`/schemes/${item.scheme_id}`} className="px-3.5 py-1.5 rounded-lg bg-emerald-600 text-slate-950 font-bold text-xs flex items-center gap-1">
                            <span>Apply Now</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Medium & Optional Priority */}
                {eligibilityResult.recommendations.medium_priority.length > 0 && (
                  <div className="glass-panel p-6 rounded-3xl border border-slate-800">
                    <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider mb-4">
                      Medium Priority Matches ({eligibilityResult.recommendations.medium_priority.length})
                    </h4>
                    <div className="space-y-3">
                      {eligibilityResult.recommendations.medium_priority.map((item: any) => (
                        <div key={item.scheme_id} className="p-3.5 rounded-xl bg-slate-900 border border-slate-850 flex items-center justify-between">
                          <div>
                            <span className="text-xs font-bold text-amber-400">{item.code}</span>
                            <h5 className="text-xs font-semibold text-white">{item.title}</h5>
                          </div>
                          <span className="text-xs font-bold text-amber-400">{item.eligibility_percentage}% Match</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
