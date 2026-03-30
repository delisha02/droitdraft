# RAG + Validation Upgrade Proposal (Best-Outcome Plan)

## Objective
Upgrade the current drafting pipeline from "prompt + evidence extraction + generation" to a legally grounded, auditable, and citation-aware system with the highest practical quality.

## Current Gap Summary
- Draft generation (`/documents/generation/generate`) does not retrieve legal context from vector/keyword stores before generation.
- Research RAG exists but is isolated from the drafting path.
- Validation is present at a high level but not yet a full legal rule engine with clause-level checks.
- Clause tagging/traceability is missing for compliance review and explainability.

## Target Architecture (Recommended)
1. User Prompt + Optional Evidence
2. Template & Clause Planner
3. Hybrid Retriever (Dense + BM25 + RRF)
4. Context Pack Builder (jurisdiction + recency + source quality filtering)
5. Clause Generator (LLM, per-clause)
6. Entity/Fact Extractor (from generated draft)
7. Legal Validation Engine (deterministic + LLM-assisted fallback)
8. Citation & Source Trace Attachment
9. Final Document + PDF/DOCX Export

## RAG vs Agentic RAG (Decision Clarification)
- **Recommended default for this product:** **RAG-assisted drafting** (non-agentic by default).
- **Why:** Most generation requests are linear and latency-sensitive; they benefit from retrieval grounding without full multi-agent orchestration overhead.
- **When to switch to agentic RAG:** only for complex matters (multi-document conflicts, citation-heavy petitions, contradictory evidence, or mandatory multi-step verification).
- **Implementation policy:**
  - Start with one deterministic generation pipeline + retrieval + validation.
  - Gate agentic mode behind a policy trigger (complexity score / user selection / template type).
  - Preserve a fast-path non-agentic route for routine notices and standard templates.



## If You Make It Completely Agentic RAG (Trade-off Analysis)
**Short answer:** possible, but not recommended as the default for all requests.

### Benefits
- Better handling of complex, multi-step legal workflows (conflict resolution, cross-document reasoning, citation reconciliation).
- Natural tool orchestration (retrieval, validator calls, policy checks, re-drafting loops).
- Stronger explainability if each agent emits traces and intermediate decisions.

### Risks / Costs
- Higher latency and token cost due to planner + multiple agent/tool turns.
- Larger failure surface (routing errors, tool timeout chains, brittle planner behavior).
- Harder QA and determinism, especially for production SLAs.
- More operational complexity (state store, retries, observability, guardrails).

### Recommended policy (best outcome)
- Keep **default path = non-agentic RAG + deterministic validation**.
- Enable **agentic mode only** when complexity triggers are met, e.g.:
  - >1 uploaded evidence document with conflicting facts,
  - citation-heavy pleading templates,
  - unresolved validator errors after one deterministic regeneration pass.
- Add a hard budget: max steps, max tokens, max wall-time; auto-fallback to deterministic RAG path.

### Minimum controls before full-agentic rollout
1. Step-level tracing and replay.
2. Strong tool contracts and schema validation between agents.
3. Circuit breakers and fallback on each tool edge.
4. Offline benchmark suite: legal accuracy, citation grounding, latency, cost.

## Required Changes (Priority Ordered)

### P0 — Integrate retrieval into draft generation route
**Why:** Largest quality gain; prevents unsupported legal statements.

- Add retrieval step inside `generate_document` before `assembly_engine.assemble_document`.
- Input query for retrieval: `case_facts.prompt`, extracted issues/statutes, and template metadata.
- Inject retrieved legal context into generation prompt under a strict section: `Grounded Legal Context`.
- Persist source IDs/URLs with the generated document metadata.

**Files to touch:**
- `backend/app/api/v1/endpoints/documents.py`
- `backend/app/services/llm_service.py`
- `backend/app/agents/document_generator/prompt_templates.py`
- `backend/app/models/models.py` (optional metadata field if needed)

### P0 — Implement actual hybrid retrieval (not config-only)
**Why:** Legal queries need both exact lexical matching (sections/citations) and semantic matching.

- Implement `get_hybrid_retriever(...)` in legal research layer.
- Compose:
  - Dense retriever: Chroma + SentenceTransformer embeddings.
  - Sparse retriever: BM25 over indexed chunks.
  - Fusion: Reciprocal Rank Fusion (RRF) with tunable `k`.
- Add weighted reranking based on:
  - jurisdiction match,
  - court level,
  - recency,
  - source reliability.

**Files to touch:**
- `backend/app/agents/legal_research/retrievers.py`
- `backend/app/core/config.py`
- `backend/app/agents/legal_research/agent.py`

### P0 — Clause tagging and per-clause generation
**Why:** Improves controllability and validation precision.

- Add clause schema (`clause_type`, `required`, `jurisdiction_rules`, `citations_required`).
- Split template into clause objects and generate clause-by-clause.
- Store provenance: which sources informed each clause.

**Files to touch:**
- `backend/app/agents/document_generator/section_generator.py`
- `backend/app/agents/document_generator/assembly_engine.py`
- new: `backend/app/agents/document_generator/clause_schema.py`

### P0 — Legal validation engine
**Why:** Core to production trust and defensibility.

- Deterministic validators:
  - required clauses present,
  - date consistency,
  - amount consistency,
  - party-role consistency,
  - jurisdiction-specific mandatory phrasing.
- Citation validators:
  - every legal proposition requiring support has at least one attached source.
  - source citation format and URL validity.
- Add confidence score + validation report in response.

**Files to touch:**
- new: `backend/app/agents/document_generator/legal_validator.py`
- `backend/app/agents/document_generator/consistency_checker.py`
- `backend/app/api/v1/endpoints/documents.py` (return validation payload)

### P1 — Evidence harmonization and conflict resolution
**Why:** Prevent contradictory draft facts from prompt vs uploaded evidence.

- Define fact precedence policy:
  1) authenticated evidence extraction,
  2) explicit user override,
  3) inferred/retrieved context.
- Add conflict log for user review UI.

**Files to touch:**
- `backend/app/agents/document_processor/llm_extractor.py`
- `backend/app/api/v1/endpoints/documents.py`
- frontend review panel integration.

### P1 — Research + drafting unification
**Why:** Single "legal memory" for both answering and drafting.

- Expose one retrieval service used by both `/research/query` and generation pipeline.
- Keep retrieval telemetry and cache hot queries.

**Files to touch:**
- new: `backend/app/services/retrieval_service.py`
- `backend/app/api/v1/endpoints/research.py`
- `backend/app/api/v1/endpoints/documents.py`

### P1 — Output traceability and explainability
**Why:** Required for lawyer trust and auditability.

- Return `clause_trace`: clause -> source chunk IDs/URLs -> validation status.
- Add "show sources" in editor next to generated clause blocks.

**Files to touch:**
- backend response schemas
- `frontend/app/editor/page.tsx`

### P2 — Agentic orchestration (targeted)
**Why:** Useful for complex documents, not required for every request.

- Use orchestrator only when:
  - multiple evidence docs,
  - conflicting facts,
  - citation-heavy petitions.
- Keep fast non-agentic path for simple notices.

**Files to touch:**
- `backend/app/agents/orchestrator/*`
- route-level policy switch.

## API Contract Additions
- `/documents/generation/generate` response should include:
  - `content`
  - `citations[]`
  - `validation_report`
  - `clause_trace[]`
  - `confidence_score`

## Data Model Additions
- Add JSON fields (or linked tables) for:
  - `retrieval_sources`
  - `validation_report`
  - `clause_trace`

## Evaluation Metrics (must-track)
1. Grounded citation precision@k
2. Missing mandatory clause rate
3. Factual inconsistency rate
4. Hallucinated legal reference rate
5. User correction rate per generated draft
6. End-to-end latency (P50/P95)

## Rollout Strategy
1. **Phase 1 (2 weeks):** Retrieval-in-generation + source attachment.
2. **Phase 2 (2–3 weeks):** Hybrid retriever + reranker + offline benchmarks.
3. **Phase 3 (2 weeks):** Clause tagging + validation engine + UI report.
4. **Phase 4 (optional):** Targeted agentic mode for complex workflows.

## Risk Controls
- Fallback to current generation path if retrieval fails.
- Strict timeout budget per stage.
- Validation failure should degrade to "draft with warnings" not silent pass.

## Definition of Done (Best-Outcome Standard)
- Drafts include traceable legal sources for critical claims.
- Mandatory clauses validated per selected template/jurisdiction.
- Evidence vs prompt conflicts surfaced to user.
- Hybrid retrieval measurably outperforms dense-only baseline.
- No major latency regression beyond agreed SLA.
