# Upgrade Execution Plan (Kickoff)

## Status
- **Kickoff started**
- Scope: Phase 0 cleanup + interface alignment before major RAG feature changes.

## Phase 0 (Current) — Cleanup and Baseline Hardening

### 0.1 Interface alignment
- [x] Add missing `get_hybrid_retriever(...)` implementation in legal research retrievers module.
- [x] Introduce retrieval service abstraction to centralize retriever construction.
- [x] Align hybrid retriever behavior and defaults with product requirements (weights, k, fusion policy).

### 0.2 Simulation and placeholder audit
- [x] Replace or isolate simulated paths in orchestrator/document export routes.
- [x] Identify dead/unused utilities and stale references.
- [x] Produce `cleanup_audit.md` with keep/remove/replace decisions.

### 0.3 Test baseline
- [x] Run focused retriever tests and fix regressions.
- [x] Add contract tests for retriever output schema.
- [ ] Add smoke test for generation route with retrieval disabled/enabled flags.

## Phase 1 — Retrieval in Draft Generation
- [x] Inject retrieval stage into `/documents/generation/generate`.
- [x] Build grounded prompt block with source metadata.
- [ ] Return draft + sources in response.

## Phase 2 — Clause + Validation
- [ ] Clause-level generation and traceability.
- [ ] Deterministic legal validation report.
- [ ] Confidence scoring and citation checks.

## Phase 3 — Targeted Agentic Mode
- [ ] Policy-gated agentic escalation for complex cases only.
- [ ] Step budgets, circuit breakers, fallback to deterministic RAG.

## Immediate next implementation ticket
1. Add smoke/integration test for generation route with retrieval disabled/enabled and verify `retrieval_sources`.
2. Begin orchestrator entrypoint consolidation (`workflow_builder`/`graph_config` vs `WorkflowEngine`) and deprecation path.
