# Specialized RAG Implementation Technical Report

## Objective
The drafting pipeline has been successfully upgraded from "standard prompt + extraction" to a legally grounded, auditable, and citation-aware system. This report details the implemented architecture and features.

## Implemented Architecture
1. **User Prompt + Optional Evidence**: Central entry point for all drafting.
2. **Template & Clause Registry**: Integrated via `maharashtra_templates.json` and a database-backed template service.
3. **Hybrid Retriever (Dense + BM25 + RRF)**: The core retrieval engine combines semantic matching (ChromaDB) with lexical matching (BM25) fused using Reciprocal Rank Fusion.
4. **Context Pack Builder**: Jurisdictional filtering and source quality prioritization.
5. **Retrieval-Augmented Drafting**: Llama 3.3-70B synthesizes content grounded in the retrieved legal context.
6. **Citation & Source Trace Attachment**: Every generated draft section is linked to verified legal authorities.

## RAG Implementation Analysis
- **Default Path**: The system uses **non-agentic RAG-assisted drafting** for primary performance and determinism.
- **Agentic Trigger**: Complex workflows (multi-document conflicts) are handled via the `WorkflowEngine` orchestrator.
- **Model Efficiency**: Leveraging **Llama 3.3-70B via Groq** to maintain sub-20s latency for full document generation.

## Key Technical Features Integrated

### Hybrid Retrieval Pipeline
- **Dense Retriever**: ChromaDB with `all-MiniLM-L6-v2` embeddings.
- **Sparse Retriever**: BM25 indexed over the legal research catalog.
- **Fusion**: RRF integration for high-precision retrieval of legal sections and citations.

### Retrieval-in-Generation Route
- Integrated into the `generate_document` pipeline.
- Input query is expanded with extracted facts and template metadata.
- Grounded legal context is injected into generation prompts under strict containment.
- Source IDs and URLs are persisted with the generated document metadata.

### Legal Validation Controls
- **Deterministic Validators**: Verification of required clauses, date consistency, and party roles.
- **Citation Validity**: Checking that legal propositions are supported by attached sources.
- **Confidence Scoring**: Implementation of response-level confidence metrics for lawyer review.

## Evaluation Metrics (Current Targets)
1. **Grounding Accuracy**: Tracking the hallucination rate (Target < 1%).
2. **Citation Relevance**: Precision@k for retrieved statutes.
3. **Latency**: Maintaining E2E latency within defined NFRs (< 20s for drafting, < 1.5s for research).

## Conclusion of Phase 3
The "Specialized RAG" architecture is now the production standard for DroitDraft, moving the platform from simple template automation to a robust, legally-grounded assistant.
