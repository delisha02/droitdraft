from typing import Any


def classify_generation_complexity(case_facts: dict[str, Any], retrieval_sources: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_count = len(case_facts.get("file_ids", []) or [])
    has_conflict_markers = any(
        bool(case_facts.get(key))
        for key in ("conflicting_facts", "disputed_facts", "fact_conflicts")
    )
    citation_heavy_hint = any(
        bool(case_facts.get(key))
        for key in ("citation_heavy", "requires_citation_rich_draft", "high_scrutiny_mode")
    )
    source_count = len(retrieval_sources or [])
    return {
        "evidence_count": evidence_count,
        "has_conflict_markers": has_conflict_markers,
        "citation_heavy_hint": citation_heavy_hint,
        "source_count": source_count,
    }


def should_escalate_agentic(
    case_facts: dict[str, Any],
    retrieval_sources: list[dict[str, Any]],
    validation_report: dict[str, Any],
    confidence_score: float,
) -> dict[str, Any]:
    complexity = classify_generation_complexity(case_facts, retrieval_sources)
    reasons: list[str] = []

    if complexity["evidence_count"] > 1:
        reasons.append("multiple_evidence_documents")
    if complexity["has_conflict_markers"]:
        reasons.append("conflicting_facts_detected")
    if complexity["citation_heavy_hint"]:
        reasons.append("citation_heavy_mode_requested")
    if validation_report.get("passed") is False:
        reasons.append("validation_failed")
    if confidence_score < 0.75:
        reasons.append("low_confidence_score")

    escalate = len(reasons) > 0
    return {
        "escalate": escalate,
        "reasons": reasons,
        "complexity": complexity,
        "step_budget": 1,
    }
