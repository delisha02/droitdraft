# 1. Introduction

## 1.1 Background Study
The legal profession has traditionally been labor-intensive, relying heavily on manual drafting, extensive research, and the precise application of statutes and precedents. Historically, "Legal Tech" in India has evolved through three distinct phases:
1.  **Legal Tech 1.0 (Digitization)**: The era of CD-ROM based case libraries and simple word processing.
2.  **Legal Tech 2.0 (Online Search)**: The rise of keyword-based search engines like Manupatra, SCC Online, and Indian Kanoon, which solved the "access" problem but not the "intelligence" problem.
3.  **Legal Tech 3.0 (Generative AI)**: The current wave, driven by Large Language Models (LLMs), which promises to automate content creation.

However, generic LLMs (like ChatGPT or Claude) fall short in the legal domain due to:
*   **Hallucinations**: They often invent non-existent case laws or cite incorrect sections, which is fatal in legal practice.
*   **Lack of Localization**: They lack deep knowledge of specific local jurisdictions, such as the *Bombay High Court Rules (Original Side)* or the *Maharashtra Rent Control Act*, often defaulting to US or UK law.
*   **Data Privacy**: Generic public models cannot be securely used with sensitive client data (e.g., divorce petitions, property deeds).

## 1.2 Motivation
The motivation behind **DroitDraft** stems from critical inefficiencies observed in the Indian legal landscape, specifically within the jurisdiction of Maharashtra:
1.  **Repetitive Labors & Burnout**: A junior lawyer spends 60-70% of their time on repetitive drafting (e.g., standard affidavits, tenancy agreements, probate petitions). This "drudgery" reduces the time available for high-level legal strategy and client interaction.
2.  **The "Hallucination" Trap**: While lawyers are eager to adopt AI, the "black box" nature of current LLMs creates a trust deficit. There is a critical need for an AI system that is "grounded" in actual, verifiable legal data—a system that can "show its work."
3.  **The Standardization Gap**: Many legal drafts in lower courts suffer from poor quality or missed procedural compliance due to a lack of standardized, high-quality precedents. A system that democratizes access to "Golden Templates" can significantly improve the quality of justice delivery.

## 1.3 Problem Statement
Legal professionals in Maharashtra face significant efficiency bottlenecks due to the manual creation of complex legal documents. Existing automated solutions are either too rigid (fill-in-the-blank templates) or too unreliable (generic generative AI).

**The Core Problem**: There is no single integrated system that combines:
1.  **Context-Aware Drafting**: The ability to draft complex documents (like Wills or Deeds) based on natural language facts and unstructured inputs (PDF evidence).
2.  **Verifiable Research**: An AI research assistant that cites *real* Indian laws and judgments with direct, clickable links to the source text.
3.  **Local Compliance**: Strict adherence to Maharashtra's specific statutes (e.g., MOFA, Maharashtra Co-op Societies Act) rather than generic central laws.

## 1.4 Proposed Solution
**DroitDraft** is an advanced, agentic AI drafting assistant designed to function as a "Virtual Senior Associate." It leverages a **Retrieval-Augmented Generation (RAG)** architecture to solve the reliability problem.

### Key Architectural Pillars:
*   **Knowledge-Grounded Generation (RAG)**: The AI does not rely solely on its training data. Instead, it dynamically accesses a curated vector database (ChromaDB) containing:
    *   **Statutes**: Full text of Central and Maharashtra State Acts.
    *   **Case Law**: 20+ years of reported judgments from the Bombay High Court and Supreme Court.
    *   **Rules**: Procedural manuals (Civil/Criminal Manuals).
*   **Specialized Agentic Workflow**:
    *   **The Researcher**: An agent dedicated to finding relevant laws.
    *   **The Draftsman**: An agent trained on "Golden Templates" to generate the document structure.
    *   **The Reviewer**: A separate agent (planned) to check for consistency and clauses.
*   **Evidence-Based Automation**: An integrated OCR and Extraction pipeline that pulls facts directly from uploaded documents (IDs, previous deeds, death certificates), minimizing manual data entry errors.
*   **"Ghost Flow" UX**: A novel user interface offering inline, autocomplete-style suggestions ("Ghost Typing") that allows lawyers to retain control while speeding up production by predicting standard legal phrasing.

## 1.5 Scope of the Project

### 1.5.1 In-Scope (Deliverables)
*   **Jurisdictional Focus**: Primary focus on laws and procedures applicable in **Maharashtra** (Bombay High Court and lower courts) and Central Indian Acts.
*   **Supported Document Categories**:
    *   **Testamentary**: Wills, Probate Petitions, Succession Certificates.
    *   **Conveyancing**: Sale Deeds, Leave & License Agreements, Gift Deeds.
    *   **Litigation**: Legal Notices (Sec 138 NI Act), Plaints for Summary Suits.
*   **Technical Features**:
    *   Hybrid RAG Search (Keyword + Semantic).
    *   Live Citation Tooltips.
    *   User Dashboard for document management.
    *   PDF/Image text extraction.

### 1.5.2 Out-of-Scope (Limitations)
*   **Legal Advice**: The system is a drafting *tool*, not a lawyer. It does not provide legal advice, strategy, or predict case outcomes (predictive justice).
*   **Full Vernacular Drafting**: While the system understands vernacular terms (e.g., "7/12 extract", "Ferfar"), full drafting capability in Marathi or Hindi is not included in this version.
*   **Automatic E-Filing**: Integration with the CIS (Case Information System) or e-Filing portals is not currently supported due to API restrictions.
