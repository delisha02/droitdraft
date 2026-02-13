# DroitDraft Evolution Roadmap

This roadmap outlines the transition from a functional document editor to a full-scale AI Legal Assistant.

## Current Progress & Status

| Feature | Implementation Status | Notes |
| :--- | :--- | :--- |
| **Multi-Document Template Library** | ✅ Completed | Seeded 6+ Maharashtra-specific templates with 50+ docs. |
| **Source Fact Extraction** | ✅ Completed | File Upload UI, MinIO, and LLM Extraction active. |
| **Integrated Legal Research Sandbox** | ✅ Completed | LiveLaw & Indian Kanoon RAG Pipeline fully functional. |
| **Legal Citation Assistant** | ✅ Completed | Natural Indian citations (Acts/Judgments) with hover-cards and "Insert to Draft". |
| **Live Legal Updates Integration** | ✅ Completed | LiveLaw Scraper automatically tracks top stories. |

---

## Phase 1: Knowledge & Extraction (Completed)
### 1.1 Maharashtra Template Library
- Seeded and verified: Public Notice, Sale Deed, Probate, Wills, Notices, and Agreements.
### 1.2 Multi-Modal Input & Fact Extraction
- [x] **File Uploads**: Support PDF/Image uploads via MinIO.
- [x] **Agent Action**: `LLMExtractor` uses Llama 3.3 to extract parties/dates for auto-filling.
- [x] **Drafting Engine**: Assembly Engine populates blueprints with evidence facts.

---

## Phase 2: Agentic RAG & Research (Nearly Completed)
### 2.1 LiveLaw & Indian Kanoon Deep Sync
- [x] **RAG Pipeline**: Persistent ChromaDB indexing Maharashtra High Court & Bombay High Court judgments (~50+ docs seeded).
- [x] **Indian Kanoon Client**: Full API integration for searching and fetching judgments via POST.
- [x] **Research Sandbox**: Integrated Editor Sidebar (Research Tab) for grounded legal Q&A.
### 2.2 Advanced Citation Engine (✅ COMPLETED)
- [x] **Grounded LLM Output**: Agent already generates citations with source titles and URLs.
- [x] **Natural Citation Formatting**: Agents use natural Indian legal formats (Section/Act/Case Reporter).
- [x] **Inline Citation Parser**: Regex-based detection of natural citations in both Research and Drafts.
- [x] **UI Hover-Cards**: Displaying source snippets when hovering over a cited judgment/section.
- [x] **Insert to Draft**: One-click transfer of cited authorities into the main editor.

---

## Phase 3: Advanced UX (The "Ghost" Flow) (✅ COMPLETED)
### 3.1 Ghost Typing (Autocomplete)
- [x] **Inline Suggestions**: AI suggests the next legal sentence in gray (Press `Tab` to accept).
- [x] **Context Awareness**: Suggestions adapt to the specific "Case Facts" extracted earlier.
### 3.2 "Insert to Draft" Integration
- [x] **One-Click Research**: Button to instantly insert a researched judgment summary or citation into the editor. (Completed in Phase 2).

---

## Phase 4 & Future Considerations (Long-Term)
### 4.1 Collaborative Drafting
- [ ] **Multi-user Sync**: Real-time collaborative editing for legal teams.
- [ ] **Comments & Track Changes**: Legal-specific review workflow.
### 4.2 Intelligent Case Tracking
- [ ] **Appellate Watch**: Automatic notification if a cited judgment is overruled or appealed.
- [ ] **Deadline Tracking**: Extract dates from notices and sync with legal calendars.
### 4.3 Court-Specific Formatting
- [ ] **PDF/A Export**: Compliant exports for e-filing in Bombay High Court and District Courts.

---

## Deployment & Development
```powershell
# Backend (Port 8000 default)
cd backend
python -m uvicorn app.main:app --reload --port 8002

# Frontend
cd frontend
npm run dev
```
