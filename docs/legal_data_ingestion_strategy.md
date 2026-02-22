# Legal Data Ingestion Strategy & Roadmap

## 1. Executive Summary
This document outlines the strategy for populating the `droitdraft` RAG database with the necessary legal corpus to support automated drafting and legal research. The current database contains a limited set of recent news summaries and scattered judgments. To become a robust legal assistant, the system requires a structured ingestion of statutes, comprehensive case law, procedural rules, and high-quality drafting precedents.

## 2. Target Jurisdictions & Scope
- **Primary Jurisdiction:** Maharashtra (Bombay High Court & Lower Courts)
- **Federal Jurisdiction:** Supreme Court of India & Central Acts
- **Core Domains:**
  - Civil Litigation (Property, Family, Contract)
  - Criminal Litigation (Bail, FIR Quashing)
  - Commercial/Corporate (Agreements, Notices)

## 3. Required Document Categories

### 3.1. Core Statutes (Bare Acts)
*Must be ingested with hierarchical metadata (Section -> Chapter -> Act).*

| Priority | Act Name | Justification |
| :--- | :--- | :--- |
| **Critical** | **Bhartiya Nyaya Sanhita (BNS) / IPC** | Core criminal substantive law. |
| **Critical** | **Bhartiya Nagarik Suraksha Sanhita (BNSS) / CrPC** | Core criminal procedure. |
| **Critical** | **Bhartiya Sakshya Adhiniyam (BSA) / Evidence Act** | Rules of evidence. |
| **Critical** | **Code of Civil Procedure (CPC)** | Essential for all civil litigation drafts. |
| **High** | **Maharashtra Rent Control Act** | Vital for tenancy disputes in Maharashtra. |
| **High** | **Maharashtra Land Revenue Code** | Essential for property title verification. |
| **High** | **Transfer of Property Act** | Foundation for Sale Deeds, Leases. |
| **High** | **Indian Contract Act** | Basis for all commercial agreements. |
| **High** | **Specific Relief Act** | Crucial for enforceability of contracts. |
| **Medium** | Hindu Succession Act / Indian Succession Act | For Wills, Probate, and Succession Certificates. |
| **Medium** | Negotiable Instruments Act (Sec 138) | Commonly used for cheque bounce cases. |

### 3.2. Case Law (Judgments)
*Focus on binding precedents and recent interpretations.*

- **Supreme Court of India:**
  - **Landmark Judgments (1950–Present):** Constitutional benches, key interpretations of core acts.
  - **Recent Judgments (Last 5 Years):** Active legal positions.
- **Bombay High Court:**
  - **Reported Judgments (Last 20 Years):** Focus on Property, Rent Control, and Family Law.
  - **Full Benches & Special Benches:** Binding on lower courts in Maharashtra.

### 3.3. Procedural Rules & Manuals
*Crucial for generating procedurally correct court filings.*

- **Bombay High Court (Original Side) Rules:** For drafting Plaints, Notices of Motion in Mumbai.
- **Bombay High Court (Appellate Side) Rules:** For Writs, Appeals.
- **Civil Manual & Criminal Manual:** Instructions for lower judiciary, often cited in procedural defenses.

### 3.4. Drafting Precedents & Templates
*Gold-standard examples for the AI to mimic.*

- **Internal Templates:** Ingest `maharashtra_templates.json` effectively.
- **External Precedents:**
  - Validated Sale Deeds, Leave & License Agreements.
  - Court Pleadings (Plaint, Written Statement, Bail Application) derived from successful cases.

---

## 4. Ingestion Sources & Methods

### 4.1. Indian Kanoon (API)
- **Role:** Primary source for Case Law.
- **Strategy:**
  - Search query for specific Acts (e.g., "Section 138 Negotiable Instruments Act").
  - Filter by `doc_type: judgment`.
  - Filter by Court (`Supreme Court`, `Bombay High Court`).

### 4.2. LiveLaw / Bar & Bench (Scrapers/RSS)
- **Role:** Recent updates, legal news, simple summaries.
- **Strategy:**
  - Continue existing scrapers for daily updates.
  - Use for "Current Awareness" but not primary legal research.

### 4.3. Official Gazettes & e-Courts Services
- **Role:** Authentic source for Bare Acts and Rules.
- **Strategy:**
  - PDF parsing of Gazettes for new notifications.
  - Manual curation of amended Bare Acts (as online versions are often outdated).

---

## 5. Processing & Storage Strategy

### 5.1. Metadata Schema
Every document in ChromaDB must have rich metadata for retrieval filtering:

```json
{
  "title": "Document Title",
  "source": "indian_kanoon | livelaw | upload | internal_template",
  "doc_type": "judgment | statute | rule | template",
  "jurisdiction": "India | Maharashtra",
  "court": "Supreme Court | Bombay High Court",
  "statute_ref": ["IPC Section 302", "CrPC Section 41A"],
  "date": "YYYY-MM-DD",
  "citation": "AIR 2024 SC 123",
  "judge": "Chandrachud CJI"
}
```

### 5.2. Chunking Strategies
- **Statutes:** Chunk by **Section**. Do not split a section across chunks if possible. Include the Chapter context in the chunk text.
- **Judgments:** Chunk by **Paragraphs** (2-3 paras), with overlap. Critical: Prepend case title and outcome to every chunk to maintain context.
- **Templates:** Chunk by **Clauses** (e.g., "Indemnity Clause", "Termination Clause") to allow the AI to mix-and-match clauses.

## 6. Roadmap

1.  **Immediate (Phase 1):** Ingest the "Core Statutes" (BNS, BNSS, BSA, CPC, Contract Act).
2.  **Short-term (Phase 2):** Ingest `maharashtra_templates.json` properly into the vector store.
3.  **Medium-term (Phase 3):** Bulk ingest 1000 landmark judgments from Indian Kanoon focusing on Civil/Criminal procedure.
4.  **Long-term (Phase 4):** Automated daily sync with LiveLaw/Indian Kanoon for new judgments.
