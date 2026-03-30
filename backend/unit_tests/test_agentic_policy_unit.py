import importlib.util
from pathlib import Path

_POLICY_PATH = Path(__file__).resolve().parents[1] / "app" / "agents" / "document_generator" / "agentic_policy.py"
_SPEC = importlib.util.spec_from_file_location("agentic_policy_under_test", _POLICY_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)


def test_should_escalate_agentic_for_complex_case():
    decision = _MODULE.should_escalate_agentic(
        case_facts={"file_ids": ["a", "b"], "citation_heavy": True},
        retrieval_sources=[{"id": "s1"}],
        validation_report={"passed": False},
        confidence_score=0.6,
    )

    assert decision["escalate"] is True
    assert "multiple_evidence_documents" in decision["reasons"]
    assert "validation_failed" in decision["reasons"]
    assert decision["step_budget"] == 1


def test_should_not_escalate_for_simple_high_confidence_case():
    decision = _MODULE.should_escalate_agentic(
        case_facts={"file_ids": []},
        retrieval_sources=[{"id": "s1"}],
        validation_report={"passed": True},
        confidence_score=0.92,
    )

    assert decision["escalate"] is False
    assert decision["reasons"] == []
