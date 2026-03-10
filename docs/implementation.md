# 6. Implementation

## 6.1 Algorithms/Methods Used

The DroitDraft system leverages a combination of deterministic algorithms (for retrieval) and probabilistic methods (for generation) to solve the legal drafting challenge.

### 6.1.1 Retrieval-Augmented Generation (RAG)
We implemented a standard RAG pipeline to ground the AI's generation in verified legal data, preventing hallucinations.

*   **Chunking Methodology**: *Recursive Character Text Splitting*
    *   **Algorithm**: Documents are split into chunks of **1000 characters** with a **200-character overlap**.
    *   **Rationale**: Legal statutes often have cross-references. Overlap ensures that a sentence split across chunks doesn't lose context.
*   **Embedding Methodology**: *Dense Vector Mapping*
    *   **Model**: We use **Sentence-BERT (all-MiniLM-L6-v2)** to map legal text to a **384-dimensional dense vector space**.
    *   **Similarity Metric**: We use **Cosine Similarity** to calculate the angle between the Query Vector and Document Vectors. The chunks with the highest cosine similarity score (closest to 1.0) are retrieved as relevant context.

### 6.1.2 Hybrid Search (Keyword + Semantic)
To improve retrieval accuracy for specific legal terms (e.g., "Section 138"), we implement a Hybrid Search strategy.

*   **Dense Retrieval**: Uses Vector Similarity (captures semantic meaning like "bounced check").
*   **Sparse Retrieval**: Uses **BM25 (Best Matching 25)** algorithm (captures exact keywords like "NI Act").
*   **Fusion Algorithm**: **Reciprocal Rank Fusion (RRF)**. We rank the results from both methods and merge them based on the formula:
    $$ RRF(d) = \sum_{r \in R} \frac{1}{k + r(d)} $$
    where $r(d)$ is the rank of document $d$ in the retrieved list $R$, and $k$ is a constant (typically 60).

### 6.1.3 Fact Extraction (NER via Generative AI)
Instead of traditional CRF-based Named Entity Recognition (like Spacy), we use **Generative Extraction**.

*   **Method**: We pass the OCR text to Llama 3 with a strict **Pydantic/JSON Schema** definition.
*   **Prompting Strategy**: **One-Shot Prompting**. We provide *one* example of a correct extraction in the system prompt to guide the model's output format, ensuring the JSON structure is always valid.

### 6.1.4 Ghost Typing (Predictive Text)
*   **Method**: **Causal Language Modeling (Next Token Prediction)**. The model predicts the most probable next sequence of tokens based on the current cursor position.
*   **Optimization Algorithm**: **Debouncing**. To prevent server overload and UI jitter, the API request is only triggered after the user stops typing for **300ms**. If the user types again within this window, the previous request is cancelled.

## 6.2 Algorithm Walkthrough on One Example Query (Single Slide Narrative)

Goal: show how one user query is transformed step-by-step by the exact algorithms used in this project.

**Example query used across all steps**

> "Draft a legal notice under Section 138 NI Act for cheque bounce. Cheque amount is ₹2,50,000, cheque date is 05 Jan 2025, return memo reason is 'insufficient funds'."

### Step 1: Generative Extraction + One-Shot Prompting - Fact Structuring

```mermaid
flowchart LR
    Q["Input Query
Section 138 cheque-bounce request"] --> EX["Generative Extraction
+ One-Shot Prompting"]
    EX --> F["Output Facts JSON
statute, amount, cheque_date, reason"]
```

- Input query text is converted into schema-valid structured facts, so downstream retrieval and drafting are deterministic.
- One-shot prompting constrains the LLM to output normalized legal fields (instead of free-form prose).

### Step 2: Recursive Character Text Splitting - Corpus Chunking

```mermaid
flowchart LR
    KB["Legal Corpus Text
acts/cases/news"] --> CH["Recursive Character
Text Splitting"]
    CH --> CK["Output Chunks
overlap-preserved units"]
```

- Corpus documents are transformed from long legal text into overlapping chunks that preserve cross-sentence legal context.
- For the example query, terms like "Section 138" and "dishonour" remain recoverable even near chunk boundaries.

**Equation / rule used**

$$ s_i = i \cdot (L - o),\; L=1000,\; o=200 $$

### Step 3: Sentence-BERT - Dense Vectorization

```mermaid
flowchart LR
    QF["Input Query/Facts Text"] --> EMBQ["Sentence-BERT"]
    CK["Input Chunks"] --> EMBD["Sentence-BERT"]
    EMBQ --> VQ["Query Vector q ∈ R^384"]
    EMBD --> VD["Chunk Vectors d ∈ R^384"]
```

- Query/facts text and chunks are mapped into the same 384-d semantic vector space.
- This transforms symbolic legal text into numeric representations usable by dense retrieval.

### Step 4: Cosine Similarity - Dense Retrieval Scoring

```mermaid
flowchart LR
    VQ["Query Vector"] --> COS["Cosine Similarity"]
    VD["Chunk Vectors"] --> COS
    COS --> DR["Dense Ranked List
semantic matches"]
```

- The example query is transformed into dense semantic scores against each chunk.
- Chunks discussing "dishonoured cheque" can rank high even if wording differs from "cheque bounce".

**Equation used**

$$
\mathrm{cos\_sim}(\mathbf{q},\mathbf{d}) =
\frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|\,\|\mathbf{d}\|}
$$

### Step 5: BM25 - Sparse Lexical Retrieval Scoring

```mermaid
flowchart LR
    TQ["Tokenized Query
Section 138, NI Act"] --> BM["BM25"]
    TD["Tokenized Chunks"] --> BM
    BM --> SR["Sparse Ranked List
keyword/legal-token matches"]
```

- The same query is transformed into lexical term-frequency signals for statute-exact matching.
- BM25 strongly rewards exact legal tokens like "Section 138" and "NI Act".

**Equation used**

$$
\mathrm{BM25}(q,d)=\sum_{t\in q}\mathrm{IDF}(t)\cdot
\frac{f(t,d)(k_1+1)}{f(t,d)+k_1\left(1-b+b\frac{|d|}{\mathrm{avgdl}}\right)}
$$

### Step 6: Reciprocal Rank Fusion (RRF) - Hybrid Rank Merge

```mermaid
flowchart LR
    DR["Dense Ranked List"] --> RRF["Reciprocal Rank Fusion"]
    SR["Sparse Ranked List"] --> RRF
    RRF --> CTX["Output: Final Ranked Context"]
```

- Dense and sparse rankings for the example query are merged into one robust context ranking.
- Documents strong in either semantic or lexical channel move up; documents strong in both usually dominate.

**Equation used**

$$
\mathrm{RRF}(d)=\sum_{r\in R}\frac{1}{k+r(d)},\; k\approx 60
$$

### Step 7: Retrieval-Augmented Generation (RAG) - Grounded Draft Synthesis

```mermaid
flowchart LR
    F["Structured Facts JSON"] --> RAG["RAG Prompt Assembly
+ LLM Generation"]
    CTX["Top-k Ranked Legal Context"] --> RAG
    RAG --> OUT["Output Draft Sections
facts, legal basis, demand clause"]
```

- The query is now transformed into a grounded draft via `Prompt = Instructions + Facts JSON + Retrieved Context`.
- Output sections remain tied to retrieved legal material, reducing hallucinated legal claims.

### Step 8 (Optional): Causal Language Modeling + Debouncing - Editor Suggestions

```mermaid
flowchart LR
    ED["User Partial Text"] --> DB["Debounce 300ms"]
    DB --> CLM["Causal LM
Next-token prediction"]
    CLM --> SG["Inline Suggestion"]
```

- During editing, partial user text is transformed into next-token suggestions for drafting speed.
- Debouncing controls request frequency, improving responsiveness and reducing noisy calls.

**Equation used**

$$ P(x_t\mid x_{<t}) = \mathrm{softmax}(z_t) $$

