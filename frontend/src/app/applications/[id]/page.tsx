"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { applicationApi } from '@/lib/api';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import Link from 'next/link';
import { CheckCircle2, AlertCircle, FileText, Download, Upload, ArrowRight, ShieldCheck, Sparkles, Building, ArrowLeft } from 'lucide-react';

export default function ApplicationJourneyPage() {
  const { id } = useParams();
  const [appDetails, setAppDetails] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploadingDoc, setUploadingDoc] = useState<boolean>(false);
  const [selectedDocType, setSelectedDocType] = useState<string>('Income Certificate');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [generatingPdf, setGeneratingPdf] = useState<boolean>(false);
  const [extraAddress, setExtraAddress] = useState<string>('45 West Car Street, Madurai');

  useEffect(() => {
    if (id) {
      loadApplication();
    }
  }, [id]);

  const loadApplication = async () => {
    setLoading(true);
    try {
      const data = await applicationApi.getApplicationDetails(id as string);
      setAppDetails(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploadingDoc(true);
    try {
      await applicationApi.uploadDocument(id as string, selectedDocType, selectedFile);
      setSelectedFile(null);
      await loadApplication();
    } catch (err) {
      console.error(err);
    } finally {
      setUploadingDoc(false);
    }
  };

  const handleGeneratePdf = async () => {
    setGeneratingPdf(true);
    try {
      await applicationApi.generateFormPdf(id as string, { address: extraAddress });
      await loadApplication();
    } catch (err) {
      console.error(err);
    } finally {
      setGeneratingPdf(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!appDetails) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col text-white">
        <Navbar />
        <div className="flex-1 flex items-center justify-center flex-col">
          <h2 className="text-xl font-bold">Application Not Found</h2>
          <Link href="/dashboard" className="mt-4 px-4 py-2 bg-emerald-600 rounded-xl text-xs font-bold text-slate-950">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const steps = [
    { key: 'eligibility_verified', title: 'Eligibility Verified' },
    { key: 'documents_pending', title: 'Upload Required Docs' },
    { key: 'ready_for_form_generation', title: 'Auto-Fill Form' },
    { key: 'ready_for_submission', title: 'Download & Submit' }
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 lg:px-8 py-10">
        <Link href="/dashboard" className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-white mb-6">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Citizen Dashboard</span>
        </Link>

        {/* Application Banner */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4 mb-3">
            <span className="px-3 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-extrabold uppercase border border-emerald-500/20">
              {appDetails.scheme.code} Application
            </span>
            <span className="text-xs text-amber-400 font-bold uppercase tracking-wider bg-amber-500/10 px-3 py-1 rounded-lg border border-amber-500/20">
              Status: {appDetails.status}
            </span>
          </div>

          <h1 className="text-2xl lg:text-3xl font-extrabold text-white mb-2">{appDetails.scheme.title}</h1>
          <p className="text-xs text-slate-400">Application ID: {appDetails.id}</p>

          {/* Stepper Bar */}
          <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-3">
            {steps.map((step, sIdx) => (
              <div
                key={step.key}
                className={`p-3 rounded-2xl border text-center transition-all ${
                  appDetails.journey_step === step.key
                    ? 'bg-emerald-600 text-slate-950 border-emerald-400 font-bold shadow-lg shadow-emerald-900/40'
                    : 'bg-slate-900 text-slate-400 border-slate-800'
                }`}
              >
                <span className="text-[10px] block uppercase tracking-wider font-extrabold opacity-80">Step {sIdx + 1}</span>
                <span className="text-xs font-semibold">{step.title}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Missing Documents Alert & Upload Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
          {/* Missing Document Checklist */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4 text-amber-400" />
              <span>Smart Document Checklist</span>
            </h3>

            {appDetails.missing_docs && appDetails.missing_docs.length > 0 ? (
              <div className="mb-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
                <span className="font-bold flex items-center gap-1.5 mb-1">
                  <AlertCircle className="w-4 h-4" />
                  Action Required: {appDetails.missing_docs.length} Missing Document(s) Detected
                </span>
                <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-300 mt-2">
                  {appDetails.missing_docs.map((doc: string, idx: number) => (
                    <li key={idx} className="font-semibold text-rose-300">{doc}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2 font-bold">
                <CheckCircle2 className="w-4 h-4" />
                <span>All Required Documents Uploaded & Verified!</span>
              </div>
            )}

            {/* Already Uploaded Docs */}
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">Verified Uploaded Documents:</h4>
            <div className="space-y-2">
              {appDetails.uploaded_documents.map((doc: any) => (
                <div key={doc.id} className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <span className="font-semibold text-white">✓ {doc.document_type} ({doc.file_name})</span>
                  <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded">OCR VERIFIED</span>
                </div>
              ))}
            </div>
          </div>

          {/* Upload Certificate Widget */}
          <div className="glass-panel p-6 rounded-3xl border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <Upload className="w-4 h-4 text-emerald-400" />
              <span>Upload Document for OCR Scan</span>
            </h3>

            <form onSubmit={handleDocumentUpload} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1">Select Document Type</label>
                <select
                  value={selectedDocType}
                  onChange={(e) => setSelectedDocType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Income Certificate">Income Certificate</option>
                  <option value="Aadhaar Card">Aadhaar Card</option>
                  <option value="Community Certificate">Community Certificate</option>
                  <option value="Ration Card">Ration Card</option>
                  <option value="Bank Passbook">Bank Passbook</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1">Attach File (PDF or Image)</label>
                <input
                  type="file"
                  required
                  onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-emerald-600 file:text-slate-950 hover:file:bg-emerald-500"
                />
              </div>

              <button
                type="submit"
                disabled={uploadingDoc || !selectedFile}
                className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-900/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {uploadingDoc ? (
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Upload & Run OCR Scan</span>
                    <Upload className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Section 3: Auto-Fill Form & PDF Download Action */}
        <div className="glass-panel p-8 rounded-3xl border border-slate-800 shadow-2xl">
          <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-400" />
            <span>Official Government Form Auto-Filler</span>
          </h3>
          <p className="text-xs text-slate-400 mb-6">
            Our AI auto-populates all official government form fields using your profile memory and OCR verified documents.
          </p>

          <div className="flex items-center justify-between flex-wrap gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-850">
            <div>
              <h4 className="text-sm font-bold text-white">Generate Official PDF Application Form</h4>
              <p className="text-xs text-slate-400 mt-1">Pre-filled with your name, income, verified document checklist, and digital seal.</p>
            </div>

            {appDetails.pdf_url ? (
              <a
                href={`http://localhost:8000${appDetails.pdf_url}`}
                target="_blank"
                rel="noreferrer"
                className="px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs shadow-lg shadow-amber-900/40 flex items-center gap-2 transition-all"
              >
                <Download className="w-4 h-4" />
                <span>Download Ready Application PDF</span>
              </a>
            ) : (
              <button
                onClick={handleGeneratePdf}
                disabled={generatingPdf}
                className="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-900/40 flex items-center gap-2 transition-all"
              >
                {generatingPdf ? (
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>Auto-Fill & Render PDF Form</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
