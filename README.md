# DroitDraft - AI-Powered Legal Platform

DroitDraft is a state-of-the-art AI-powered legal document generation platform. This repository is a monorepo containing both the FastAPI backend and the Next.js frontend.

## Prerequisites

- **Docker**: For running the PostgreSQL database.
- **Python 3.9+**: For the backend.
- **Node.js 18+**: For the frontend.
- **Git**: For version control.

---

## 1. Environment Setup (Docker)

The project relies on three key Docker services:
- **PostgreSQL**: Primary data store for users and templates.
- **MinIO**: S3-compatible storage for uploaded evidence files.
- **ChromaDB**: Vector database for legal research and RAG.

1. **Start all required containers**:
   ```powershell
   docker start postgres_db compassionate_buck great_banzai
   ```

2. **Database Permissions** (First-time setup):
   ```powershell
   docker exec -it postgres_db psql -U droitdraft_user -d droitdraft_dev -c "GRANT ALL ON SCHEMA public TO droitdraft_user;"
   ```

---

## 2. Backend Setup

1. **Navigate to backend**: `cd backend`
2. **Setup Venv**: `python -m venv .venv` and activate it.
3. **Install Core**: `pip install -r requirements.txt`
4. **Environment**: Create `.env`. Ensure `GROQ_API_KEY` and `GEMINI_API_KEY` are present.
5. **Seeding**: To load the professional Maharashtra templates:
   ```powershell
   python scripts/seed_db.py
   ```
6. **Run**: `uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload`

---

## 3. Frontend Setup

1. **Navigate to frontend**: `cd frontend`
2. **Install**: `npm install`
3. **Run**: `npm run dev -- -p 3001`
   *Available at `http://localhost:3001`*

---

## 🚀 Key Features Implemented

- **Agentic Drafting Flow**: Powered by **Llama 3.3 (Groq)**, the system drafts documents using professional legal blueprints.
- **Maharashtra Template Library**: Pre-loaded with 10+ verified proformas for Wills, Sale Deeds, Probate Petitions, and Legal Notices.
- **Evidence-Grounded Drafting**: Upload PDF/Image evidence (Death Certificates, IDs). The "Senior Associate" Agent extracts facts and auto-fills the blueprints.
- **Smart Editor**: Markdown-to-HTML rendering with automatic date injection and noise removal for a 100% professional output.
- **JWT & Session Security**: Long-lived sessions (24h) with secure JWT authentication.