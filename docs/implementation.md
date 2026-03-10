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

Goal: Show, step-by-step, how a user query is transformed at every stage of the DroitDraft pipeline, with concrete intermediate values and outputs.

**Example Query:**

> "Draft a legal notice under Section 138 NI Act for cheque bounce. Cheque amount is ₹2,50,000, cheque date is 05 Jan 2025, return memo reason is 'insufficient funds'."

---


### Step 1: Fact Extraction (Generative Extraction + One-Shot Prompting)

**Input:**
```
Draft a legal notice under Section 138 NI Act for cheque bounce. Cheque amount is ₹2,50,000, cheque date is 05 Jan 2025, return memo reason is 'insufficient funds'.
```

**Transformation:**
The query is passed to Llama 3 with a one-shot prompt and a strict JSON schema.

**Diagram:**
```mermaid
flowchart LR
        Q["User Query"] --> |"LLM + One-Shot Prompt"| FJ["Extracted Facts JSON"]
```

**Output (Extracted Facts JSON):**
```json
{
    "statute": "Section 138 NI Act",
    "amount": 250000,
    "cheque_date": "2025-01-05",
    "dishonour_reason": "insufficient funds",
    "task": "draft_legal_notice"
}
```

---


### Step 2: Passage Chunking (Recursive Character Text Splitting)

**Input:**
Relevant legal text (e.g., Section 138 NI Act):
```
Section 138. Dishonour of cheque for insufficiency, etc., of funds in the account... payee may make a demand for the payment... within 15 days of receiving information... etc.
```

**Transformation:**
Split into overlapping chunks (L=1000, overlap=200):

**Equation:**
$$ s_i = i \cdot (L - o),\; L=1000,\; o=200 $$

**Diagram:**
```mermaid
flowchart LR
    P["Legal Passage"] --> |"Chunking"| C1["Chunk 1"]
    P --> |"Chunking (overlap)"| C2["Chunk 2"]
```

**Output (Chunks):**
```
Chunk 1: "Section 138. Dishonour of cheque for insufficiency... payee may make a demand..."
Chunk 2: "...may make a demand for the payment... within 15 days of receiving information..."
```

---


### Step 3: Dense Vectorization (Sentence-BERT)

**Input:**
- Query facts text: "Section 138 cheque bounce insufficient funds"
- Chunks from Step 2

**Transformation:**
Encode both query and chunks into 384-dimensional vectors.

**Diagram:**
```mermaid
flowchart LR
    QF["Facts Text"] --> |"Sentence-BERT"| VQ["Query Vector (q)"]
    C1["Chunk 1"] --> |"Sentence-BERT"| VD1["Chunk Vector (d₁)"]
    C2["Chunk 2"] --> |"Sentence-BERT"| VD2["Chunk Vector (d₂)"]
```

**Output:**
```
Query vector q ∈ ℝ³⁸⁴
Chunk vectors d₁, d₂ ∈ ℝ³⁸⁴
```

---


### Step 4: Dense Retrieval Scoring (Cosine Similarity)

**Input:**
- Query vector q
- Chunk vectors d₁, d₂

**Transformation:**
Compute cosine similarity between q and each dᵢ.

**Equation:**
$$
\mathrm{cos\_sim}(\mathbf{q},\mathbf{d}) =
\frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|\,\|\mathbf{d}\|}
$$

**Diagram:**
```mermaid
flowchart LR
    VQ["Query Vector (q)"] --> |"Cosine Similarity"| S1["Score 1"]
    VD1["Chunk Vector (d₁)"] --> S1
    VQ --> |"Cosine Similarity"| S2["Score 2"]
    VD2["Chunk Vector (d₂)"] --> S2
```

**Output (Sample Scores):**
```
cos_sim(q, d₁) = 0.82
cos_sim(q, d₂) = 0.77
```
**Dense Ranked List:**
1. Chunk 1 (0.82)
2. Chunk 2 (0.77)

---


### Step 5: Sparse Lexical Retrieval (BM25)

**Input:**
- Tokenized query: ["section", "138", "ni", "act", "cheque", "bounce"]
- Tokenized chunks

**Transformation:**
BM25 scores based on token overlap and term statistics.

**Equation:**
$$
\mathrm{BM25}(q,d)=\sum_{t\in q}\mathrm{IDF}(t)\cdot
\frac{f(t,d)(k_1+1)}{f(t,d)+k_1\left(1-b+b\frac{|d|}{\mathrm{avgdl}}\right)}
$$

**Diagram:**
```mermaid
flowchart LR
    TQ["Tokenized Query"] --> |"BM25"| B1["BM25 Score 1"]
    TD1["Tokenized Chunk 1"] --> B1
    TQ --> |"BM25"| B2["BM25 Score 2"]
    TD2["Tokenized Chunk 2"] --> B2
```

**Output (Sample Scores):**
```
BM25(q, d₁) = 4.2
BM25(q, d₂) = 3.7
```
**Sparse Ranked List:**
1. Chunk 1 (4.2)
2. Chunk 2 (3.7)

---


### Step 6: Hybrid Rank Merge (Reciprocal Rank Fusion)

**Input:**
- Dense ranked list: Chunk 1 > Chunk 2
- Sparse ranked list: Chunk 1 > Chunk 2

**Transformation:**
Apply RRF to merge rankings.

**Equation:**
$$
\mathrm{RRF}(d)=\sum_{r\in R}\frac{1}{k+r(d)},\; k\approx 60
$$

**Diagram:**
```mermaid
flowchart LR
    DR["Dense Ranking"] --> |"RRF"| F1["Fused Rank"]
    SR["Sparse Ranking"] --> |"RRF"| F1
```

**Output (Fused Context Ranking):**
1. Chunk 1
2. Chunk 2

---


### Step 7: Prompt Assembly & Draft Generation (RAG)

**Input:**
- Extracted Facts JSON
- Top-k retrieved context chunks

**Transformation:**
Prompt template is filled:
```
INSTRUCTIONS: Draft a legal notice using the facts and legal context below.
FACTS: {Facts JSON}
CONTEXT: {Top-k Chunks}
```
Passed to LLM for generation.

**Diagram:**
```mermaid
flowchart LR
    FJ["Facts JSON"] --> |"Prompt Assembly"| PR["Prompt"]
    CTX["Top-k Chunks"] --> PR
    PR --> |"LLM"| OUT["Draft Notice"]
```

**Output (Draft Excerpt):**
```
"Dear Sir/Madam,\n\nYou have issued a cheque dated 05 Jan 2025 for ₹2,50,000, which was returned unpaid due to insufficient funds. As per Section 138 of the NI Act, you are hereby called upon to pay the amount within 15 days of receipt of this notice..."
```

---


### Step 8 (Optional): Editor Suggestion (Ghost Typing)

**Input:**
Partial draft: "You are hereby called upon to pay..."

**Transformation:**
After 300ms pause, next-token prediction is triggered.

**Equation:**
$$ P(x_t \mid x_{1:t-1}) = \mathrm{softmax}(z_t) $$

**Diagram:**
```mermaid
flowchart LR
    PD["Partial Draft"] --> |"Debounce 300ms"| CLM["Causal LM"]
    CLM --> SUG["Suggestion"]
```

**Output:**
Suggestion: "within 15 days of receipt of this notice."

---

**Summary Table: Example Query Transformation**

| Step | Input | Output |
|------|-------|--------|
| 1 | User query | Facts JSON |
| 2 | Legal text | Chunks |
| 3 | Facts, Chunks | Vectors |
| 4 | Vectors | Dense ranking |
| 5 | Tokens | Sparse ranking |
| 6 | Rankings | Fused context |
| 7 | Facts, Context | Draft |
| 8 | Partial draft | Suggestion |

