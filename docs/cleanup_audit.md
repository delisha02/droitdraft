# Cleanup Audit (Commit C)

## Scope
- Targeted Phase 0.2 cleanup for simulated/stale execution paths in orchestrator + generation-adjacent flows.
- Focus on low-risk fixes that unblock production hardening without changing external API contracts.

## Findings and Actions

| Area | File(s) | Finding | Decision | Action in Commit C |
|---|---|---|---|---|
| Orchestrator input processing | `backend/app/agents/orchestrator/agent_nodes.py` | `document_processor_node` used hardcoded `template_id=1` and `"Maharashtra Rent Control Act"` research query, which bypassed caller intent and looked like test scaffolding in production path. | **Replace** | Removed hardcoded assignments. Node now requires caller-provided `template_id` and only derives fallback `research_query` from structured facts when possible. |
| Orchestrator DB lifecycle | `backend/app/agents/orchestrator/agent_nodes.py` | `get_template_node` opened DB session via `next(deps.get_db())` without deterministic cleanup. | **Replace** | Wrapped DB usage in `try/finally` and close session in all cases. |
| State contract drift | `backend/app/agents/orchestrator/state_manager.py` | `document_processor_node` referenced `document_id` fallback, but state contract did not declare it. | **Keep + align** | Added optional `document_id` to `DroitAgentState` for schema clarity. |
| Legacy graph path | `backend/app/agents/orchestrator/workflow_builder.py`, `backend/app/agents/orchestrator/graph_config.py` | Legacy builder path still exists alongside `WorkflowEngine` dynamic JSON path. | **Keep (for now)** | No functional change in this commit; retain to avoid breaking graph bootstrap import path. Marked for later consolidation. |

## Deferred Items (Next Cleanup PR)
1. Consolidate orchestrator execution entrypoints (`workflow_builder`/`graph_config` vs `WorkflowEngine`) behind one canonical runtime path.
2. Add focused orchestrator unit tests for:
   - missing `template_id` rejection in `document_processor_node`,
   - DB session close behavior in `get_template_node`,
   - fallback `research_query` derivation.
3. Standardize logging/error handling in endpoints (`print` -> structured logger).
