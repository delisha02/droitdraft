# 3. System Analysis

## 3.1 Functional Requirements

### FR 1: Document Processing & Fact Extraction
*   **FR 1.1**: The system must allow users to upload PDF/Image documents (e.g., Death Certificates, Previous Deeds) as evidence.
    *   **Input**: PDF/JPG/PNG files up to 25MB.
    *   **Process**: OCR (Tesseract/Google Vision) and Text Cleaning.
    *   **Output**: Structured JSON containing raw text and metadata.
*   **FR 1.2**: The system must extract key entities (Names, Dates, Addresses, Relationships) from uploaded documents.
    *   **Input**: Raw OCR Text.
    *   **Process**: LLM-based Named Entity Recognition (NER) with specific schema enforcement (Pydantic).
    *   **Output**: Validated JSON object (e.g., `{ "party_name": "Ramesh Kumar", "dob": "1980-01-01" }`).
*   **FR 1.3**: The system must provide a UI for users to verify and correct extracted facts.
    *   **Input**: Extracted JSON.
    *   **Process**: Render editable form fields. Sync updates to state.
    *   **Output**: Verified Fact Sheet ready for drafting.

### FR 2: Legal Drafting & Generation
*   **FR 2.1**: The system must provide a library of Maharashtra-specific templates.
    *   **Input**: User selection (Jurisdiction > Doc Type).
    *   **Process**: Fetch template schema from Database.
    *   **Output**: Template form with specific fields (e.g., "Flat No.", "CTS No.").
*   **FR 2.2**: The system must generate a first draft by populating templates.
    *   **Input**: Template ID + Verified Fact Sheet.
    *   **Process**: Variable substitution (Jinja2) or LLM-based expansion for complex clauses.
    *   **Output**: Functional legal draft in the Editor.
*   **FR 2.3**: The system must support "Ghost Typing" (Context-Aware Autocomplete).
    *   **Input**: Current cursor context (last 1000 chars) + Extracted Facts.
    *   **Process**: High-speed LLM inference (Groq/Llama3) to predict next tokens.
    *   **Output**: Inline shadow text suggestion (e.g., "...and the Licensee shall pay...").

### FR 3: Retrieval-Augmented Research (RAG)
*   **FR 3.1**: The system must maintain a vector database of legal documents.
    *   **Data**: Indian Statutes, Bombay High Court Judgments.
    *   **Update Frequency**: Weekly sync with sources.
*   **FR 3.2**: The system must answer legal queries with citations.
    *   **Input**: Natural language query (e.g., "Can a tenant be evicted without notice?").
    *   **Process**: Hybrid Search (Vector + Keyword) -> LLM Synthesis -> Citation Linking.
    *   **Output**: Answer with [1][2] citations linking to source text.

## 3.2 Non-Functional Requirements

### NFR 1: Accuracy & Reliability
*   **NFR 1.1 - Hallucination Rate**: < 1% for legal citations. The system must refuse to answer if no relevant documents are found.
*   **NFR 1.2 - Extraction Accuracy**: > 90% for clear, typed text documents (standard 300 DPI scans).

### NFR 2: Data Security & Privacy (ISO 27001 Compliant)
*   **NFR 2.1 - Encryption**: AES-256 for data at rest (MinIO/Postgres). TLS 1.3 for data in transit.
*   **NFR 2.2 - Data Residency**: All client data must be stored on servers located within India (Digital Personal Data Protection Act, 2023 compliance).
*   **NFR 2.3 - Access Control**: Role-Based Access Control (RBAC) ensuring users can only access their own case files.

### NFR 3: Performance & Scalability
*   **NFR 3.1 - Drafting Latency**: Full document generation < 15 seconds.
*   **NFR 3.2 - Ghost Typing Latency**: Suggestion appearance < 400ms (to feel "instant").
*   **NFR 3.3 - Concurrent Users**: Support 50+ concurrent drafting sessions on standard hardware.

---

## 3.3 Specific Requirements

### 3.3.1 Software and Hardware Requirements

**Software Stack:**
*   **Frontend**: Next.js 14 (React Server Components), Tailwind CSS, Shadcn UI.
*   **Backend**: Python 3.11, FastAPI (Async), Celery (Task Queue).
*   **Database**: PostgreSQL 16 (Relation), ChromaDB 0.4 (Vector), Redis 7 (Cache).
*   **AI Orchestration**: LangChain 0.1, LlamaIndex (for pdf parsing).
*   **OCR Engine**: Tesseract 5 / Google Cloud Vision API.

**Hardware Specifications (Minimum Server Req):**
*   **CPU**: 8 vCPUs (Intel Xeon / AMD EPYC) for vector calculations.
*   **RAM**: 32 GB (16GB for Vector Index in-memory, 8GB for App, 8GB OS).
*   **Storage**: 500GB NVMe SSD (High IOPS required for Vector Search).
*   **Network**: 1Gbps Uplink.

---

## 3.4 Use-Case Diagrams and Description

*(Refer to Analysis Modeling Document for detailed Diagrams)*

### Description of Key Use Cases

| Use Case ID | Use Case Name | Actor | Description |
| :--- | :--- | :--- | :--- |
| **UC-01** | **Upload Evidence** | Lawyer | User uploads files (PDF/Img). System validates format, scans for malware, performs OCR, and extracts structured data. |
| **UC-02** | **Generate Draft** | Lawyer | User selects a specific template. System maps extracted data to template fields. User reviews mapping. System generates draft. |
| **UC-03** | **Ghost Typing** | Lawyer | As user types in the editor, system continuously predicts the next 3-5 words based on legal context and extracted facts. |
| **UC-04** | **Legal Research** | Lawyer | User asks a question ("Limitation period?"). System retrieves relevant statutes/judgments, synthesizes an answer, and provides verified citations. |

---

## 3.5 Sequence Diagram (Draft Generation)

*(See Design Document for Sequence Diagram)*
