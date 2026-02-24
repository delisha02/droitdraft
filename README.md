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

### Phase 1: Knowledge & Extraction
- **Maharashtra Template Library**: 7 verified proformas for Wills, Sale Deeds, Probate Petitions, and Legal Notices.
- **Evidence-Grounded Drafting**: Upload PDF/Image evidence (Death Certificates, IDs). The AI extracts facts and auto-fills the templates.
- **MinIO Storage**: Secure S3-compatible storage for uploaded evidence files.

### Phase 2: Agentic RAG & Research
- **Legal Research Sandbox**: Interactive sidebar for real-time legal Q&A using RAG.
- **ChromaDB Vector Store**: 56+ legal documents indexed for research.
- **Natural Legal Citations**: AI cites Acts and Sections naturally (e.g., "Section 10 of the Indian Contract Act, 1872").
- **Insert to Draft**: One-click transfer of cited authorities into the editor.

### Phase 3: Advanced UX (Ghost Flow)
- **Ghost Typing**: AI-powered inline autocomplete that suggests the next legal sentence in gray text.
- **Tab-to-Accept**: Press `Tab` to accept AI suggestions instantly.
- **Context-Awareness**: Suggestions adapt based on the current draft and extracted case facts.

### Core Features
- **Agentic Drafting Flow**: Powered by **Llama 3.3 (Groq)** with Gemini fallback.
- **Smart Editor**: Markdown-to-HTML rendering with automatic date injection.
- **JWT & Session Security**: Long-lived sessions (24h) with secure JWT authentication.

---

## 📄 Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)**: Comprehensive verification guide for all features.
- **[roadmap.md](roadmap.md)**: Development roadmap and future plans.
- **[docs/system_architecture_diagram.md](docs/system_architecture_diagram.md)**: Highly detailed architecture diagrams (platform, runtime sequence, and ingestion pipeline).
