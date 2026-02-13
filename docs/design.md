# 5. Design

## 5.1 Architectural Design

DroitDraft follows a modern **Service-Oriented Architecture (SOA)** with a clear separation between the client-side presentation, server-side business logic, and the intelligence layer. This decoupled approach allows for independent scaling of the drafting engine and the research engine.

### System Components:

1.  **Frontend Layer (Next.js 14)**:
    *   **Role**: Handles User Interaction, State Management, and Real-time Editor rendering.
    *   **Key Components**:
        *   `EditorProvider`: Manages the rich-text state and ghost typing overlays.
        *   `PDFViewer`: Integrated viewer for side-by-side evidence review.
        *   `ChatInterface`: WebSocket connection for low-latency research queries.
2.  **Backend Layer (FastAPI)**:
    *   **Role**: Orchestrates all business logic, database interactions, and AI agent chaining.
    *   **Key Modules**:
        *   `DraftingAgent`: Routes requests to the Llama 3 model for text generation.
        *   `ResearchAgent`: Executes the RAG pipeline.
        *   `AuthMiddleware`: JWT validation and RBAC enforcement.
3.  **Data Layer**:
    *   **PostgreSQL**: Stores relational data (Users, Templates, Draft Metadata).
    *   **MinIO**: High-performance object storage for evidence files (S3 compatible).
    *   **ChromaDB**: Vector store for semantic search indices.
4.  **Async Task Queue (Celery + Redis)**:
    *   **Role**: Handles computationally expensive tasks off the main thread (e.g., OCR processing of large PDFs, periodic scraping of Indian Kanoon).

```mermaid
graph TD
    Client[Client Browser] <-->|HTTPS/REST| Frontend[Next.js Frontend]
    Frontend <-->|API Calls| Backend[FastAPI Backend]
    
    subgraph Data Persistence
    Backend -->|Read/Write| DB[(PostgreSQL)]
    Backend -->|Vector Search| VectorDB[(ChromaDB)]
    Backend -->|File Storage| ObjectStore[MinIO]
    end
    
    subgraph Async Processing
    Backend -->|Enqueue Task| Queue[Redis Broker]
    Queue -->|Consume Task| Worker[Celery Worker]
    Worker -->|OCR/Scraping| ExtServices[External APIs]
    end
    
    Backend <-->|Inference| LLM_API[LLM Provider (Groq)]
```

## 5.2 Models Explored

### 5.2.1 Rationale for Model Selection

The selection of AI models was driven by the specific, often conflicting, constraints of legal drafting:
1.  **Context Window**: Legal documents are long. A typical Sale Deed can be 20 pages. We needed models with at least 32k token context to "read" the whole document.
2.  **Inference Speed**: Ghost typing requires near-instantaneous (<200ms) latency to feel natural.
3.  **Reasoning Capability**: Legal analysis requires high logical reasoning (IRAC method - Issue, Rule, Analysis, Conclusion), not just creative writing.
4.  **Data Privacy**: Preference for open-weights models that can be self-hosted or used via private endpoints.

### 5.2.2 Models Architecture Evaluated

We evaluated three primary classes of models:

1.  **GPT-4o (OpenAI)**:
    *   *Pros*: Best-in-class reasoning, huge context (128k).
    *   *Cons*: Expensive ($5/1M tokens), variable latency, data privacy concerns.
2.  **Claude 3.5 Sonnet (Anthropic)**:
    *   *Pros*: Excellent nuance in writing, fewer refusals.
    *   *Cons*: Cost, strict rate limits.
3.  **Llama 3-70B (Meta) on Groq LPU**:
    *   *Pros*: **Blazing fast speed (~300 tokens/s)**, low cost, open weights allowing fine-tuning.
    *   *Cons*: Smaller context window (8k in early versions, now extended).

For **Embeddings** (RAG), we explored:
1.  **OpenAI `text-embedding-3-small`**: High quality but paid.
2.  **HuggingFace `all-MiniLM-L6-v2`**: Local, fast (384 dimensions), free.
3.  **BAAI `bge-m3`**: Multilingual, 1024 dimensions, state-of-the-art.

### 5.2.3 Evaluation and Comparison

| Feature | GPT-4o | Claude 3.5 | Llama 3 (Groq) | **Selected** |
| :--- | :--- | :--- | :--- | :--- |
| **Legal Reasoning** | 92/100 | 94/100 | 85/100 | **Llama 3** (Adequate) |
| **Speed (Tokens/s)** | ~40 | ~30 | **~300** | **Llama 3** (Winner) |
| **Cost / 1M Tokens** | ~$5.00 | ~$3.00 | **<$0.70** | **Llama 3** (Winner) |
| **Privacy Control** | Low | Medium | **High** | **Llama 3** (Winner) |

*Decision*: We selected **Llama 3-70B running on Groq** as the primary engine. The speed advantage is non-negotiable for the "Ghost Typing" feature, and the reasoning gap is bridged by the RAG architecture which provides the model with the exact legal text it needs to cite.

## 5.3 User Interface Design

The UI is designed to minimize cognitive load ("Focus Mode") while providing powerful tools on demand ("Cockpit Mode").

### 1. The Dashboard (Case Management)
*   **Card-Based Layout**: Visual summaries of recent drafts with progress bars (e.g., "Drafting", "Review", "Finalized").
*   **Quick Actions**: "New Draft", "Upload Evidence" buttons.

### 2. The Split-Screen Editor (The Cockpit)
*   **Left-Pane (The Canvas)**: A clean, distraction-free rich text editor (Tiptap based) that mimics Microsoft Word but with AI superpowers.
*   **Right-Pane (The Assistant)**: A collapsible sidebar (30% width) containing:
    *   **Chat**: For natural language instructions ("Rewrite clause 4 to be more strict").
    *   **Research**: For querying the RAG database.
    *   **Facts**: A verified list of extracted entities that can be dragged and dropped.

### 3. Ghost Typing (Interaction Design)
*   **Visual Cue**: Suggestions appear in `gray (#A0A0A0)` text *ahead* of the cursor.
*   **Interaction**:
    *   `Tab`: Accepts the suggestion.
    *   `Esc` or `Type Any Key`: Dismisses the suggestion immediately.
*   **Feedback**: A subtle, non-intrusive spinner in the corner indicates when the AI is "thinking" to avoid distracting the user.
