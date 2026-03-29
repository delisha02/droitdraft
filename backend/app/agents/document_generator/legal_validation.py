import re
from typing import Any


_CITATION_PATTERNS = [
    r"\bSection\s+\d+[A-Za-z\-]*\b",
    r"\bArticle\s+\d+[A-Za-z\-]*\b",
    r"\b[A-Z][A-Za-z\s]+Act,\s*\d{4}\b",
]


def split_into_clauses(document: str) -> list[dict[str, Any]]:
    """Deterministically split generated content into numbered clause blocks."""
    raw_clauses = [line.strip() for line in (document or "").splitlines() if line.strip()]
    clauses: list[dict[str, Any]] = []
    for idx, clause_text in enumerate(raw_clauses, start=1):
        clauses.append(
            {
                "clause_id": f"C{idx}",
                "clause_index": idx,
                "text": clause_text,
            }
        )
    return clauses


def extract_citations(text: str) -> list[str]:
    citations: list[str] = []
    for pattern in _CITATION_PATTERNS:
        citations.extend(re.findall(pattern, text or ""))
    # deterministic unique ordering
    seen = set()
    unique = []
    for item in citations:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def build_clause_traceability(document: str, retrieval_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clauses = split_into_clauses(document)
    source_ids = [src.get("id") for src in retrieval_sources if src.get("id")]
    for clause in clauses:
        citations = extract_citations(clause["text"])
        clause["citations"] = citations
        # Deterministic linkage: if clause contains citations and sources exist, attach all ids.
        # If no citations, leave linkage empty for explicit traceability.
        clause["supporting_source_ids"] = source_ids if citations else []
    return clauses


def build_citation_checks(document: str) -> dict[str, Any]:
    clauses = split_into_clauses(document)
    clause_results = []
    missing_citation_clause_ids = []
    for clause in clauses:
        citations = extract_citations(clause["text"])
        has_citation = len(citations) > 0
        clause_results.append(
            {
                "clause_id": clause["clause_id"],
                "has_citation": has_citation,
                "citations": citations,
            }
        )
        if not has_citation:
            missing_citation_clause_ids.append(clause["clause_id"])
    return {
        "total_clauses": len(clauses),
        "clauses_with_citations": len(clauses) - len(missing_citation_clause_ids),
        "missing_citation_clause_ids": missing_citation_clause_ids,
        "per_clause": clause_results,
    }


def build_validation_report(document: str, retrieval_sources: list[dict[str, Any]]) -> dict[str, Any]:
    clauses = split_into_clauses(document)
    citation_checks = build_citation_checks(document)
    issues = []
    if not clauses:
        issues.append("generated_document_empty")
    if citation_checks["clauses_with_citations"] == 0 and clauses:
        issues.append("no_legal_citations_detected")
    if retrieval_sources and citation_checks["clauses_with_citations"] == 0:
        issues.append("retrieval_present_but_not_used_in_clauses")

    return {
        "passed": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "total_clauses": len(clauses),
        "total_retrieval_sources": len(retrieval_sources),
        "citation_summary": {
            "clauses_with_citations": citation_checks["clauses_with_citations"],
            "total_clauses": citation_checks["total_clauses"],
        },
    }


def compute_confidence_score(validation_report: dict[str, Any], citation_checks: dict[str, Any]) -> float:
    """
    Deterministic confidence score in [0, 1].
    Weighted by validation pass/fail and citation coverage.
    """
    total = max(citation_checks.get("total_clauses", 0), 1)
    coverage = citation_checks.get("clauses_with_citations", 0) / total
    base = 0.7 if validation_report.get("passed") else 0.4
    score = base + (0.3 * coverage)
    return round(min(max(score, 0.0), 1.0), 3)
