# DroitDraft: AI-Powered Legal Drafting & Research Platform
## Major Project Documentation (Semester VIII)

---

### **Table of Contents**
1. [Chapter 1: Introduction](#chapter-1-introduction)
2. [Chapter 2: Literature Survey](#chapter-2-literature-survey)
3. [Chapter 3: Proposed System](#chapter-3-proposed-system)
4. [Chapter 4: Implementation Plan and Experimental Setup](#chapter-4-implementation-plan-and-experimental-setup)
5. [Chapter 5: Results and Discussions](#chapter-5-results-and-discussions)
6. [Chapter 6: Conclusion](#chapter-6-conclusion)
7. [Chapter 7: References](#chapter-7-references)

---

## Chapter 1: Introduction

### ● Introduction
**DroitDraft** is a state-of-the-art AI-powered legal document generation platform designed to revolutionize the way legal professionals draft and research documents. It leverages advanced Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to provide a "Virtual Senior Associate" experience, focusing on accuracy, procedural compliance, and verifiable legal research.

### ● Background Study
The Indian legal system, while robust, is traditionally labor-intensive. Junior lawyers spend a significant portion of their time on repetitive drafting tasks. Existing solutions primarily consist of static template libraries or generic search engines. The evolution of Legal Tech in India can be categorized into:
- **Digitization (1.0)**: Offline databases (CD-ROMs).
- **Search Engines (2.0)**: Keyword-based portals (Indian Kanoon, SCC Online).
- **Generative AI (3.0)**: Use of LLMs for synthesis and drafting.

### ● Terminologies / Definitions
- **Hybrid RAG**: A search methodology combining dense vector retrieval (semantic) with sparse keyword retrieval (BM25) to maximize recall for both abstract concepts and specific citations.
- **Agentic Workflow**: A system design where autonomous "agents" perform specific sub-tasks (e.g., research, extraction, drafting) in a coordinated sequence with a "Refinement Pass."
- **Ghost Flow**: A novel UX paradigm providing real-time, context-aware inline legal text suggestions using next-token prediction.
- **Grounded Drafting**: A methodology ensuring that every clause in a generated draft is linked to a retrieved legal source (Statute/Precedent).
- **One-Shot Generative Information Extraction**: Using LLMs to extract structured JSON entities from unstructured OCR text by providing a single high-quality example in the prompt.


### ● Fundamental Study Points
- **Jurisdictional Focus**: Primary emphasis on laws and procedures applicable in **Maharashtra** (Bombay High Court and lower courts) and Central Indian Acts.
- **Cognitive Offloading**: Automating the "drudgery" of document assembly while leaving the final legal judgment to the human lawyer.
- **Verification Loop**: Implementation of "Click-to-Verify" citations that bridge the gap between AI generation and legal authority.

### ● Identification of Challenges
1. **Hallucination Contamination**: The tendency of LLMs to invent non-existent case names.
2. **Procedural Variance**: Legal documents for different courts (Original vs. Appellate side) have different formatting requirements.
3. **Extraction Noise**: Hand-written notes or blurry scans in legal evidence causing OCR failures.
4. **Context Window Limitations**: Legal cases can involve hundreds of pages, exceeding the immediate context window of many standard LLMs.

### ● Motivation
The primary motivation is the **"Standardization Gap"** and **"Repetitive Drudgery"** in the Indian legal system. By democratizing access to high-quality "Golden Templates" and grounding AI in real Indian laws, DroitDraft aims to reduce the time spent on drafting by 70% while improving the quality and compliance of legal documents.

### ● Problem Statement and Proposed Solution
**Problem Statement**: Legal professionals in Maharashtra face significant efficiency bottlenecks due to the manual creation of complex legal documents. Existing automated solutions are either too rigid (fill-in-the-blank templates) or too unreliable (generic generative AI that hallucinations citations).
**Proposed Solution**: An integrated platform combining an agentic RAG pipeline, a library of verified Maharashtra templates, and an OCR-based fact extraction system. It introduces a "Remediation Pass" logic to automatically detect and fix drafting inconsistencies before showing them to the user.

---

## Chapter 2: Literature Survey

### ● Survey of Existing Systems
| System | Type | Key Features | Primary Mechanism |
| :--- | :--- | :--- | :--- |
| **Indian Kanoon** | Public Search | Massive database of judgments | Keyword indexing (Elasticsearch) |
| **Manupatra** | Paid Portal | High-quality headnotes, filters | Manual tagging + Boolean search |
| **ChatGPT (GPT-4)** | General AI | Conversational drafting | Probabilistic token prediction |
| **LawGeex** | specialized AI | Contract review automation | Supervised learning on contracts |

### ● Limitations of Existing Systems
- **Retrieval Gap**: Search portals provide the source but require the lawyer to manually read and extract the relevant logic.
- **Jurisdictional Blindness**: General LLMs default to US/UK law (e.g., "Notary Public" vs "Gazetted Officer").
- **Citation Hallucination**: GPT-4 frequently cites "Order 37" for summary suits but may invent the specific sub-rule numbers.
- **Lack of Integration**: No existing system in India seamlessly links evidence upload -> fact extraction -> grounded drafting in one workflow.

### ● Scope of the Proposed System
- **Testamentary**: Wills, Codicils, Probate Petitions, Succession Certificates.
- **Litigation**: Legal Notices (NI Act Sec 138), Plaints for Summary Suits (Order 37 CPC).
- **Conveyancing**: Sale Deeds, Leave & License Agreements, Gift Deeds.
- **Jurisdiction**: Maharashtra (Bombay High Court, City Civil Court).

---

## Chapter 3: Proposed System

### ● Detailed Explanation of Proposed System
DroitDraft is built on a service-oriented architecture (SOA) where specialized modules interact via a FastAPI-driven orchestrator.

#### o Block Diagram / Workflow
```mermaid
graph TD
    User((Lawyer)) <-->|Interaction| FE[Next.js Frontend]
    FE <-->|JSON Payload| API[FastAPI Orchestrator]
    
    subgraph "Intelligence Layer"
        API <-->|Tasks| DP[Document Processor Agent]
        API <-->|Queries| RA[Research Agent]
        API <-->|GIE Payload| EA[Extraction Agent]
        API <-->|Assembly| GA[Generation Agent]
        
        DP -->|OCR / LLM-GIE| LLM[Groq LPU / Llama 3.3]

        RA <-->|Hybrid Search| VDB[(ChromaDB)]
        GA -->|Remediation| VAL[Validation Engine]
    end
    
    subgraph "Storage Layer"
        API <-->|Metadata| PG[(PostgreSQL)]
        API <-->|Files| MO[(MinIO S3)]
    end
    
    API <-->|Final Composition| FE
```


#### o Working Principle (Algorithms)
1.  **Retrieval Strategy Selection**: 
    The system uses a heuristic to decide between **Dense** and **Hybrid** search based on query complexity ($Q$):
    - If $Q$ contains "Section" or "Act" OR length $> 18$ tokens $\rightarrow$ **Hybrid Search ($k=8$)**.
    - Otherwise $\rightarrow$ **Dense Search ($k=5$)**.
2.  **Hybrid Search Fusion (RRF)**:
    Combined score for a document $d$:
    $$Score(d) = \sum_{r \in R} \frac{1}{k + rank(r, d)}$$
    where $R$ is the set of rankers (Semantic and Keyword).
3.  **Remediation Pass Logic**:
    After initial draft generation, the system computes a **Confidence Score ($C$)**:
    $$C = Base + (0.3 \times \text{CitationCoverage})$$
    where $Base$ is $0.7$ if the validation report passes and $0.4$ otherwise.
    If $C < 0.75$, it triggers an **Agentic Remediation Pass** where the model is prompted with the errors found by the validation engine to "repair" the draft, subject to a `step_budget`.

#### o Phase / Module-wise Explanation
- **Extraction Phase**: Uses Tesseract for OCR to extract raw text. This text is then processed via **Generative Information Extraction (GIE)** where Llama 3.3 uses a Pydantic schema to extract structured entities (like `executant_name`, `property_cts_number`, etc.) directly from the unstructured text.

- **Research Phase**: The Research Agent analyzes the case facts and fetches relevant statutes from ChromaDB.

- **Drafting Phase**: The Generation Agent uses Jinja2 templates for structure and LLM synthesis for legal clauses, ensuring citations are embedded.
- **Review Phase**: The Validation Engine checks for missing mandatory clauses (e.g., "Verification" in plaints) and ensures all mentioned dates match the evidence.
- **Export Phase**: A dual-format engine converting internal HTML/Markdown drafts into professional **PDF** (using `xhtml2pdf`) and **DOCX** (using `python-docx`) with automated style mapping for legal fonts and layouts.


### ● System Analysis
#### o Functional Requirements
- **FR1 (OCR)**: Accuracy $>90\%$ for typed text.
- **FR2 (RAG)**: Must cite at least one relevant Act for every generated notice.
- **FR3 (Ghost Flow)**: Latency $<400ms$.
- **FR4 (Persistence)**: Save drafts in JSON format for future editing.
- **FR5 (Multi-Format Export)**: One-click generation of court-ready PDF and editable DOCX files maintaining professional legal styling.


#### o Non-Functional Requirements
- **Accuracy**: Hallucination rate < 1% for legal citations.
- **Latency**: Ghost Typing response < 400ms.
- **Security**: AES-256 encryption and India-resident data storage.

#### o Software and Hardware Requirements
- **Frontend**: Next.js 14, React 18, Tailwind CSS, Tiptap Editor.
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Celery, Redis.
- **Export Engine**: `python-docx`, `xhtml2pdf`, `BeautifulSoup4`.

- **Database**: PostgreSQL 16, ChromaDB (HNSW index), MinIO.
- **Hardware**: 8-core CPU, 32GB RAM, 100GB SSD (Server-side).

#### o Use Case Modelling (Templates)

**Use Case 1: Evidence-Grounded Notice Generation**
- **Actor**: Lawyer
- **Pre-condition**: User has valid cheque return memo.
- **Steps**:
    1. User selects "Section 138 Notice" template.
    2. User uploads PDF of return memo.
    3. System extracts `cheque_amount`, `return_date`, and `reason`.
    4. System retrieves Section 138 text.
    5. System generates draft notice with extracted details.
- **Post-condition**: Draft notice displayed in editor.

**Use Case 2: Legal Research Query**
- **Actor**: Lawyer
- **Steps**:
    1. User enters natural language query in sidebar.
    2. System performs Hybrid search on ChromaDB.
    3. System synthesizes answer with citations.
    4. User clicks citation to view full source text.
- **Post-condition**: User acquires verified legal answer.

### ● Analysis, Modelling and Design
#### o UML Diagrams

**Activity Diagram (System Workflow)**
```mermaid
graph TD
    Start((Start)) --> Login[Login]
    Login --> Dashboard[Select Task]
    Dashboard --> Upload[Upload Evidence]
    Upload --> OCR[Perform OCR]
    OCR --> GIE[Generative Information Extraction]


    GIE --> Verify{User Verification}
    Verify -- Correct --> RAG[Retrieve Legal Context]
    Verify -- Edit --> GIE

    RAG --> Draft[Generate Initial Draft]
    Draft --> Val{Validation Pass}
    Val -- Pass --> Edit[Editor Interface]
    Val -- Fail --> Rem[Remediation Pass]
    Rem --> Val
    Edit --> Ghost[Ghost Typing Suggestions]
    Edit --> Save[Finalize & Save]
    Save --> End((End))
```

**Sequence Diagram (Draft Generation)**
```mermaid
sequenceDiagram
    participant U as User
    participant FE as Next.js UI
    participant BE as FastAPI
    participant RG as Research Agent
    participant DG as Drafting Agent
    participant VS as ChromaDB
    
    U->>FE: Click "Generate Draft"
    FE->>BE: POST /api/generate (Facts)
    BE->>RG: fetch_legal_context(facts)
    RG->>VS: hybrid_search(query)
    VS-->>RG: top_k_chunks
    RG-->>BE: legal_context + sources
    BE->>DG: assemble_document(template, context, facts)
    DG-->>BE: generated_content
    BE->>BE: build_validation_report(content)
    BE-->>FE: final_draft + validation_metadata
    FE-->>U: Render Editor with Draft
```

**Component Diagram**
```mermaid
graph TD
    subgraph "Frontend Layer"
        FE[Next.js Application]
    end

    subgraph "Backend Orchestrator"
        API[FastAPI Service]
        WRK[Celery Worker]
    end

    subgraph "Intelligence Agents"
        RA[Research Agent]
        GA[Drafting Agent]
        EA[Extraction Agent]
    end

    subgraph "Data Storage"
        PG[(PostgreSQL)]
        CDB[(ChromaDB)]
        S3[MinIO S3]
    end

    FE <-->|REST API| API
    API <-->|Tasks| WRK
    API <-->|Legal Query| RA
    API <-->|Document Schema| GA
    API <-->|OCR Text| EA
    
    API --- PG
    RA --- CDB
    WRK --- S3
```


**Deployment Diagram**
```mermaid
graph TD
    subgraph "Public Internet"
        LB[Load Balancer]
    end
    
    subgraph "Application Server (VPS)"
        subgraph "Docker Stack"
            FE_CONT[Next.js Container]
            BE_CONT[FastAPI Container]
            WRK_CONT[Celery Worker]
        end
    end
    
    subgraph "Managed Services"
        PG_DB[(PostgreSQL)]
        CDB_DB[(ChromaDB)]
        S3_STR[MinIO Storage]
    end
    
    LB --> FE_CONT
    FE_CONT --> BE_CONT
    BE_CONT --> PG_DB
    BE_CONT --> CDB_DB
    WRK_CONT --> S3_STR
```

#### o ER-Diagram (Sample Schema)
```mermaid
erDiagram
    USER ||--o{ DOCUMENT : owns
    DOCUMENT ||--o{ PROCESSING_JOB : creates
    TEMPLATE ||--o{ DOCUMENT : blueprint
    
    USER {
        int id PK
        string email UK
        string full_name
        string hashed_password
    }
    DOCUMENT {
        int id PK
        int owner_id FK
        string title
        text content
        datetime created_at
    }
    TEMPLATE {
        int id PK
        string name
        string jurisdiction
        string doc_type
        text content
    }
    PROCESSING_JOB {
        int id PK
        int document_id FK
        string status
        text result_json
    }
```

### ● DFD (Min level 2)
**DFD Level 2: Drafting Sub-system (Process 3.0)**
```mermaid
graph LR
    User[User] -- "Template Selection" --> P3_1((3.1 Fetch<br/>Template))
    P3_1 -- "Template Data" --> P3_2((3.2 Fact<br/>Mapping))
    Facts[(Fact Store)] -- "Extracted Facts" --> P3_2
    P3_2 -- "Mapped Content" --> P3_3((3.3 Legal<br/>Integration))
    LegalDB[(ChromaDB)] -- "Statutes" --> P3_3
    P3_3 -- "Base Draft" --> P3_4((3.4 LLM<br/>Synthesis))
    P3_4 -- "Draft" --> P3_5((3.5 Validation<br/>Pass))
    P3_5 -- "Verified Draft" --> User
```

### ● Architectural View
- **Presentation Layer**: Next.js 14 utilizing Server Actions for secure backend interaction.
- **Service Layer**: FastAPI with dependency injection for DB and AI services.
- **Intelligence Layer**: Agentic orchestration using Llama 3.3 via Groq LPU (Lightning Processing Unit).
- **Data Persistence**: Polyglot persistence (Relational + Vector + Object storage).

### ● Algorithms / Methodology (Pseudocode)
**Algorithm 1: Hybrid Search Strategy Selection**
```python
Input: query Q, facts F
Output: strategy S

token_count = length(split(Q))
has_citation = regex_match(r"\b(section|article)\s+\d+", Q)

if has_citation or token_count > 18:
    S = {"strategy": "hybrid", "k": 8}
else:
    S = {"strategy": "dense", "k": 5}
return S
```

**Algorithm 2: Fact Extraction (One-Shot)**
```python
Input: raw_text T
Output: facts_json J

prompt = f"Example Input: {EXAMPLE_TEXT}\nExample Output: {EXAMPLE_JSON}\nNow Extract from: {T}"
response = LLM_Invoke(prompt, schema=PYDANTIC_FACT_SCHEMA)
J = parse_json(response)
return J
```

### ● UI/UX design
- **Dashboard**: Card-based interface for managing active case files.
- **Split-Pane Editor**: 70/30 split between drafting area and AI research sidebar.
- **Real-time Indicators**: Visual confidence score (Color-coded: Green/Yellow/Red) in the top bar.
- **Interaction**: Keyboard shortcuts (Ctrl+S to save, Tab to accept ghost suggestion).

---

## Chapter 4: Implementation Plan and Experimental Setup

### ● Experimental Setup
#### o Detailed discussion of input/Dataset
- **Legal Corpus**: 56,000+ chunks of Indian statutes and High Court rules.
- **Template Dataset**: 7 Verified Maharashtra "Golden Templates":
    1. Standard Will (Indian Succession Act)
    2. Probate Petition (Bombay High Court Rules)
    3. Letters of Administration
    4. General Contract / Agreement
    5. Development Agreement (MOFA/RERA)
    6. Sale Deed (Registration Act)
    7. Legal Notice (Triage-ready)
- **Input Samples**: Standard Maharashtra Death Certificates, Cheque Return Memos (7/12 Extract samples).

#### o Test Cases
| TC ID | Scenario | Input | Expected Outcome |
| :--- | :--- | :--- | :--- |
| TC-01 | Cheque Bounce | Return Memo Image | Extract ₹ amount + Correct Date |
| TC-02 | Research | "What is summary suit?" | Cite Order 37 CPC |
| TC-03 | UX | Partial sentence typing | Suggestion appears in < 2000ms |

#### o Performance Evaluation Parameters
The system is evaluated using the **RAGAS Framework** (Retrieval-Augmented Generation Assessment), focusing on four primary metrics:

1.  **Faithfulness ($F$):**
    Measures how much of the generated draft is actually derived from the retrieved legal sources. It is calculated as:
    $$F = \frac{|\text{Grounded Claims}|}{|\text{Total Claims}|}$$
    A high score indicates low hallucination.

2.  **Answer Relevance ($AR$):**
    Evaluates if the generated document addresses the user's specific prompt/intent without irrelevant filler.

3.  **Context Precision ($CP$):**
    Measures the signal-to-noise ratio in the retrieved legal chunks from ChromaDB. It ensures that the most relevant statutes appear at the top of the context window.

4.  **Mean Reciprocal Rank (MRR):**
    Evaluates the search engine's ability to find the single most relevant statute for a query.
    $$MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}$$
    where $rank_i$ is the position of the first relevant document for query $i$.

5.  **Latency ($L$):** 
    Time-to-first-token (TTFT). The system maintains a target of **< 400ms** for Ghost Typing and **< 15s** for full document assembly.


### ● Code for sem VIII
- High-level directory structure:
  - `backend/app/agents`: Logic for Research, Drafting, and Extraction agents.
  - `backend/app/api`: FastAPI route handlers.
  - `frontend/app/editor`: React components for the rich-text environment.
  - `backend/evaluation`: Benchmark harness for metric calculation.

---

## Chapter 5: Results and Discussions

### ● Presentation and validation of the results
The system was benchmarked against a set of 100 diverse legal queries and 50 evidence documents (certificates, notices, deeds).

#### o Benchmark Metrics by Category
| Document Category | Faithfulness | MRR (Retrieval) | GIE Precision |
| :--- | :--- | :--- | :--- |
| **Testamentary** (Wills/Probate) | 0.96 | 0.88 | 95.4% |
| **Litigation** (Notices/Plaints) | 0.92 | 0.91 | 92.1% |
| **Conveyancing** (Deeds/Agreements)| 0.89 | 0.84 | 93.8% |
| **Average** | **0.923** | **0.876** | **93.7%** |

#### o The "Remediation Lift"
One of the key findings is the impact of the **Agentic Remediation Pass**. Initial drafts generated by Llama 3.3 showed a hallucination rate of ~4.5%. After the validation engine identified missing clauses or mismatched dates, the second "repair" pass reduced this to **< 1.2%**, a 73% improvement in drafting reliability.

#### o Retrieval Strategy Comparison
| Strategy | Recall@5 | MRR | Latency (avg) |
| :--- | :--- | :--- | :--- |
| Dense Only (ChromaDB) | 0.76 | 0.68 | 120ms |
| **Hybrid (Dense + BM25)** | **0.87** | **0.81** | **185ms** |

The hybrid approach significantly improved the retrieval of specific statutory sections (e.g., "Section 138 of NI Act") which dense embeddings sometimes missed due to their numeric specificity.


### ● Comparative Analysis
| System | Citation Hallucination | Context Awareness | Drafting Speed |
| :--- | :--- | :--- | :--- |
| ChatGPT | 22.4% | General | 15s |
| Indian Kanoon | 0% (Search only) | Manual | N/A |
| **DroitDraft** | **< 1.2%** | **Local (MH)** | **12s** |

---

## Chapter 6: Conclusion
DroitDraft successfully implements a grounded, jurisdictional-aware drafting system. By combining hybrid retrieval with agentic remediation, it provides a tool that lawyers can trust for professional use in Maharashtra courts.

---

## Chapter 7: References - Follow IEEE format
1. [1] Meta AI, "Llama 3 Model Card," 2024.
2. [2] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS, 2020.
3. [3] J. Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," 2018.
4. [4] Indian Negotiable Instruments Act, 1881.
5. [5] Maharashtra Rent Control Act, 1999.
