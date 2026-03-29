import importlib.util
from pathlib import Path

_VALIDATION_PATH = Path(__file__).resolve().parents[1] / "app" / "agents" / "document_generator" / "legal_validation.py"
_SPEC = importlib.util.spec_from_file_location("legal_validation_under_test", _VALIDATION_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)


def test_clause_traceability_attaches_source_ids_when_citation_present():
    doc = "1. Pursuant to Section 138 of the Negotiable Instruments Act, 1881."
    sources = [{"id": "src-1"}, {"id": "src-2"}]

    trace = _MODULE.build_clause_traceability(doc, sources)

    assert trace[0]["clause_id"] == "C1"
    assert "Section 138" in trace[0]["citations"][0]
    assert trace[0]["supporting_source_ids"] == ["src-1", "src-2"]


def test_validation_report_and_confidence_are_deterministic():
    doc = "This clause has no legal citation"
    sources = [{"id": "src-1"}]

    citation_checks = _MODULE.build_citation_checks(doc)
    report = _MODULE.build_validation_report(doc, sources)
    score = _MODULE.compute_confidence_score(report, citation_checks)

    assert report["passed"] is False
    assert "retrieval_present_but_not_used_in_clauses" in report["issues"]
    assert 0.0 <= score <= 1.0
