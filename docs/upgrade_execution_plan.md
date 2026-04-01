# Upgrade Execution Plan (Kickoff)

## Status
- **Kickoff started**
- Scope: Phase 0 cleanup + interface alignment before major RAG feature changes.

## Phase 0 (Current) — Cleanup and Baseline Hardening

### 0.1 Interface alignment
- [x] Add missing `get_hybrid_retriever(...)` implementation in legal research retrievers module.
- [ ] Align hybrid retriever behavior and defaults with product requirements (weights, k, fusion policy).

### 0.2 Simulation and placeholder audit
- [ ] Replace or isolate simulated paths in orchestrator/document export routes.
- [ ] Identify dead/unused utilities and stale references.
- [ ] Produce `cleanup_audit.md` with keep/remove/replace decisions.

### 0.3 Test baseline
- [ ] Run focused retriever tests and fix regressions.
- [ ] Add contract tests for retriever output schema.
- [ ] Add smoke test for generation route with retrieval disabled/enabled flags.

## Phase 1 — Retrieval in Draft Generation
- [ ] Inject retrieval stage into `/documents/generation/generate`.
- [ ] Build grounded prompt block with source metadata.
- [ ] Return draft + sources in response.

## Phase 2 — Clause + Validation
- [ ] Clause-level generation and traceability.
- [ ] Deterministic legal validation report.
- [ ] Confidence scoring and citation checks.

## Phase 3 — Targeted Agentic Mode
- [ ] Policy-gated agentic escalation for complex cases only.
- [ ] Step budgets, circuit breakers, fallback to deterministic RAG.

## Immediate next implementation ticket
1. Verify hybrid retriever with unit tests.
2. Introduce retrieval service abstraction used by both research and generation paths.
