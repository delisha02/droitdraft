# 4. Analysis Modeling

## 4.1 Activity Diagram

The following Activity Diagram illustrates the detailed workflow of a user creating a legal draft using DroitDraft.

```mermaid
stateDiagram-v2
    [*] --> Login
    Login --> Dashboard: Successful Authentication
    Dashboard --> CreateNew: Select 'New Document'
    CreateNew --> SelectTemplate: Choose Jurisdiction (MH) & Doc Type
    SelectTemplate --> UploadEvidence: Optional
    
    state "Evidence Processing Phase" as EP {
        UploadEvidence --> OCR_Scan: Tesseract/Vision API
        OCR_Scan --> ExtractFacts: LLM-based NER
        ExtractFacts --> ValidateFacts: User Review Interface
    }
    
    UploadEvidence --> ManualEntry: Skip Upload
    ValidateFacts --> GenerateDraft
    ManualEntry --> GenerateDraft
    
    state "Drafting Phase" as DP {
        GenerateDraft --> EditorView: Render Initial Draft
        EditorView --> GhostTyping: User Types -> Suggestion
        GhostTyping --> LegalResearch: User Query -> RAG Search
        LegalResearch --> InsertCitation: Insert Link [1]
        InsertCitation --> EditorView
        EditorView --> Finalize: Save/Export
    }
    
    Finalize --> DownloadPDF: Generate PDF
    Finalize --> SaveToDashboard: JSON Backup
    SaveToDashboard --> [*]
```

## 4.2 Functional Modeling (Data Flow Diagrams)

### 4.2.1 DFD Level 0 (Context Diagram)

The Level 0 DFD depicts the entire DroitDraft system as a single black-box process interacting with external entities.

*   **Inputs**: User uploads PDF Evidence, Instructions; Admin updates Rules.
*   **Outputs**: Drafted Documents, Search Results, Logs.
*   **External Entities**: 
    *   **User**: Providing instructions.
    *   **Legal Sources**: Indian Kanoon (Case Law), LiveLaw (Updates).
    *   **Cloud Storage**: Storing evidence files.

```mermaid
flowchart LR
    User[Lawyer/User]
    System((DroitDraft System))
    ExtSource[Legal Data Sources]
    Storage[Cloud Storage]

    User -- "Uploads Evidence, Instructions" --> System
    System -- "Drafted Document, Search Results" --> User
    
    System -- "Queries Citations/Judgments" --> ExtSource
    ExtSource -- "Case Law, Statutes" --> System
    
    System -- "Stores Files (Encrypted)" --> Storage
    Storage -- "Retrieves Files" --> System
```

### 4.2.2 DFD Level 1 (High-Level Subsystems)

This diagram decomposition breaks the system into four major subsystems:

1.  **Auth & User Mgmt**: Handles JWT tokens, role-based access.
2.  **Document Processing**: OCR, Cleaning, Fact Extraction pipeline.
3.  **Drafting Engine**: Template mapping, Variable substitution, Ghost Typing inference.
4.  **Legal Research (RAG)**: Vector embedding, Semantic search, Citation retrieval.

```mermaid
flowchart TD
    User[User]
    
    subgraph DroitDraft Core
        P1((1. Auth &<br/>User Mgmt))
        P2((2. Document<br/>Processing))
        P3((3. Drafting<br/>Engine))
        P4((4. Legal<br/>Research))
        DB[(PostgreSQL)]
        VectorDB[(ChromaDB)]
    end
    
    User -- "Login/Register" --> P1
    P1 -- "User Profile" --> DB
    
    User -- "Upload PDF" --> P2
    P2 -- "Extracted Facts (JSON)" --> P3
    
    User -- "Select Template" --> P3
    P3 -- "Fetch Template Schema" --> DB
    P3 -- "Generate Draft" --> User
    
    User -- "Search Query" --> P4
    P4 -- "Retrieve Context" --> VectorDB
    P4 -- "Citations" --> User
```

### 4.2.3 DFD Level 2 (Detailed Process Breakdown)

#### Process 2: Document Processing Pipeline
Input: Raw PDF -> Output: Structured JSON.

```mermaid
flowchart LR
    Input[PDF Upload] --> P2_1((2.1 OCR<br/>Extraction))
    P2_1 -- "Raw Text" --> P2_2((2.2 Entity<br/>Recognition))
    P2_2 -- "Entities (Named)" --> P2_3((2.3 Fact<br/>Mapper))
    
    Schema[(Template<br/>Schema)] -- "Field Types" --> P2_3
    P2_3 --> Output[Structured JSON]
```

#### Process 4: Legal Research (RAG) Pipeline
Input: Query -> Output: Answer with Citations.

```mermaid
flowchart LR
    Query[User Query] --> P4_1((4.1 Query<br/>Embedding))
    P4_1 --> P4_2((4.2 Semantic<br/>Hybrid Search))
    
    VectorDB[(ChromaDB)] -- "Relevant Chunks" --> P4_2
    P4_2 -- "Context + Query" --> P4_3((4.3 LLM<br/>Synthesis))
    P4_3 -- "Answer" --> Answer[Legal Answer<br/>with Citations]
```

## 4.3 Timeline Chart

The project development is divided into two academic terms involving distinct phases of research, prototype development, and advanced feature integration.

### Term I: Research & Core Development

| Phase | Duration | Key Milestones | Status |
| :--- | :--- | :--- | :--- |
| **Literature Survey & Prob. Def.** | Aug 1 - Aug 30 | Problem Statement, Scope, Lit. Review | Completed |
| **System Analysis & Design** | Sep 1 - Sep 30 | SRS, UML Diagrams, Tech Stack Selection | Completed |
| **Prototype Implementation** | Oct 1 - Oct 31 | Basic UI, Auth, Database Setup | Completed |
| **Phase 1: Knowledge Base** | Nov 1 - Dec 15 | Template Library, Basic OCR | Completed |

### Term II: Advanced Features & Deployment

| Phase | Duration | Key Milestones | Status |
| :--- | :--- | :--- | :--- |
| **Phase 2: RAG & Research** | Jan 1 - Feb 15 | ChromaDB Integration, Legal Research Agent | **In Progress** |
| **Phase 3: Advanced UX** | Feb 16 - Mar 15 | Ghost Typing, Interactive Sidebar | Planned |
| **Testing & Optimization** | Mar 16 - Mar 31 | Unit Tests, Load Testing, Bug Fixes | Planned |
| **Final Documentation & Report** | Apr 1 - Apr 15 | Final Report, User Manual, Presentation | Planned |

```mermaid
gantt
    title DroitDraft Development Timeline
    dateFormat  YYYY-MM-DD
    section Term I
    Literature Survey       :done,    des1, 2025-08-01, 2025-08-30
    System Design           :done,    des2, 2025-09-01, 2025-09-30
    Prototype Impl.         :done,    des3, 2025-10-01, 2025-10-31
    Phase 1 Knowledge       :active,  des4, 2025-11-01, 2025-12-15
    section Term II
    Phase 2 RAG & Research  :active,  dev1, 2026-01-01, 2026-02-15
    Phase 3 Advanced UX     :         dev2, 2026-02-16, 2026-03-15
    Testing                 :         dev3, 2026-03-16, 2026-03-31
    Final Report            :         dev4, 2026-04-01, 2026-04-15
```
