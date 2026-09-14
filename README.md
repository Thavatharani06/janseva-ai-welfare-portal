# JanSeva AI - Multilingual Legal Welfare Assistant Platform

Production-grade, offline-first enterprise AI platform helping Indian citizens explore government welfare schemes, calculate eligibility, simplify legal documents via ELI10 ("Explain Like I'm 10"), auto-fill government application forms, detect missing documents, detect scam queries, and interact via multilingual voice (Tamil, English, Hindi).

---

## 🌟 Key Features

1. **Multilingual Voice AI Assistant**: Voice-to-text & text-to-voice query handling in Tamil, English, and Hindi.
2. **Scheme Alias Intelligence Engine**: Fuzzy & exact matching across acronyms, local nicknames, and localized titles (e.g. `PMAY` <-> `வீடு கட்ட உதவி` <-> `Pradhan Mantri Awas Yojana`).
3. **Explain Like I'm 10 (ELI10)**: Instant 3-way toggle between Official Legal Summary, Plain Language, and Child-Friendly analogies.
4. **Interactive Eligibility Meter**: 10-parameter demographic evaluation with percentage match, reasons for eligibility, and reasons for rejection.
5. **AI Life Event Reasoner**: Semantic natural language understanding mapping life events ("My husband passed away", "My daughter is joining engineering", "I lost my job") to relevant welfare programs.
6. **Smart Application Assistant & Form Generator**: Auto-detects missing documents and auto-populates government application forms downloadable as PDF.
7. **100% Source Transparency**: Displays AI Confidence %, Government Order (G.O.) numbers, document names, page numbers, similarity metrics, and retrieved context chunks.
8. **Scam Warning Engine**: Identifies bribery or cash demands, flagging alerts with official government helplines (1100, 155261).
9. **Offline Village Mode**: Local SQLite/Chroma vector database & local LLM integration allowing complete offline deployment without cloud dependency.
10. **Admin Portal & System Analytics**: Admin controller for uploading PDFs, managing scheme aliases, and monitoring district-wise citizen analytics.

---

## 🏗️ Architecture & Technology Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Framer Motion.
- **Backend**: FastAPI, Async SQLAlchemy 2.0, Pydantic V2, PyJWT, Asyncpg / SQLite.
- **RAG & AI**: Vector Embedding Cosine Search, Ollama Local LLM / Local Generator fallback, PyTesseract & pdfplumber OCR.
- **Form Generation**: ReportLab PDF Engine.

---

## 🚀 Quick Start with Docker

```bash
# Clone and start the complete full-stack environment
docker-compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI API & OpenAPI Docs**: `http://localhost:8000/docs`

---

## 🧪 Running Backend Automated Test Suite

```bash
cd backend
python -m pytest
```
