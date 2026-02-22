# 7. Testing

## 7.1 Test Strategy

The testing strategy for DroitDraft focuses on validating the accuracy of legal content, the reliability of the RAG pipeline, and the responsiveness of the user interface.

### 7.1.1 Test Environment

| Component | Specification |
| :--- | :--- |
| **OS** | Windows 11 Pro / Ubuntu 22.04 LTS |
| **Browser** | Chrome v120+, Edge v120+, Firefox v115+ |
| **Database** | PostgreSQL 16 (Local Docker Container) |
| **LLM Provider** | Groq API (Llama 3-70B) |
| **Network** | 100 Mbps stable connection (required for RAG) |

## 7.2 Test Cases

### 7.2.1 Authentication & User Management

| TC ID | Test Description | Input Data | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | **User Registration** | Valid Email, Password (>8 chars) | Account created, User redirected to Dashboard. Email confirmation sent. | Pass |
| **TC-02** | **Invalid Login** | Unregistered Email or Wrong Password | Error message: "Invalid credentials". No session token issued. | Pass |
| **TC-03** | **Access Protected Route** | Navigate to `/editor` without login | Redirect to `/login` page. | Pass |
| **TC-04** | **Session Timeout** | Idleness > 60 mins | User logged out automatically. Token invalidated. | Pass |

### 7.2.2 Document Processing (OCR & Extraction)

| TC ID | Test Description | Input Data | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-05** | **PDF Upload** | Valid PDF (<10MB) | File stored in MinIO, shown in Dashboard. Status: "Processed". | Pass |
| **TC-06** | **Large File Upload** | PDF File (>25MB) | Error: "File exceeds 25MB limit". Upload rejected. | Pass |
| **TC-07** | **Entity Extraction** | Death Certificate (Sample 1) | Extracted: Name="Ramesh Kumar", Date="12-05-2024". JSON Validated against Schema. | Pass |
| **TC-08** | **Blurry Image OCR** | Low-res Image of ID Card | System prompts: "Image quality too low for extraction". Fallback to manual entry. | Pass |
| **TC-09** | **Malicious File Upload** | `.exe` renamed as `.pdf` | System detects MIME type mismatch and rejects upload. | Pass |

### 7.2.3 Legal Drafting Engine

| TC ID | Test Description | Input Data | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-10** | **Template Selection** | Select "Sale Deed (Maharashtra)" | Editor opens with correct columns/clauses for Sale Deed. | Pass |
| **TC-11** | **Auto-Populate Draft** | Extracted Facts (Buyer, Seller) | Names correctly inserted into Parties clause. Formatting retained. | Pass |
| **TC-12** | **Ghost Typing Trigger** | Type "The Vendor agrees to" | Suggestion: "...indemnify the Purchaser against all claims." (Latency < 400ms) | Pass |
| **TC-13** | **Missing Variable** | Template has `{{rent_amount}}` but fact is missing | System highlights the field in Red: "[ENTER RENT AMOUNT]". | Pass |

### 7.2.4 Retrieval-Augmented Generation (RAG)

| TC ID | Test Description | Input Data | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-14** | **Standard Legal Query** | "What is limit for Cheque Bounce notice?" | Answer: "30 days (Sec 138 NI Act)". Citation provided. | Pass |
| **TC-15** | **Hallucination Check** | "Case of Batman vs Superman (India)" | Answer: "No such case law found." (Does not invent case). | Pass |
| **TC-16** | **Citation Verification** | Hover over Citation [1] | Tooltip shows: "AIR 2023 SC 456". Click opens full text. | Pass |
| **TC-17** | **Jurisdictional Filter** | Query "Rent control eviction" + Filter "Maharashtra" | Answer sites *Maharashtra Rent Control Act*, NOT *Delhi Rent Control Act*. | Pass |

### 7.2.5 Performance Testing

| TC ID | Test Description | Input Data | Expected Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-18** | **Draft Generation Speed** | Generate "Will" (5 pages) | Completed in < 10 seconds. | Pass |
| **TC-19** | **Search Latency** | Complex Query (Hybrid Search) | Results retrieved in < 3 seconds. | Pass |
| **TC-20** | **Concurrent Load** | 50 Users Drafting simultaneously | Server CPU < 80%, No dropped connections. | Pass |
## 7.3 Automated Status Verification

For a quick check of the system's core components (PostgreSQL, ChromaDB, and Legal Research Agent), use the provided verification script.

### 7.3.1 Running the Verification Script

1. Open a terminal in the project root.
2. Run the following command:
   ```powershell
   .\.venv\Scripts\python.exe verify_project_status.py
   ```

### 7.3.2 What it verifies:
- **PostgreSQL**: Integrity of User, Template, and Document counts.
- **ChromaDB**: Total number of legal documents indexed for RAG.
- **Legal Research Agent**: End-to-end test of query processing, context retrieval from ChromaDB, and LLM (Groq) answer generation.
