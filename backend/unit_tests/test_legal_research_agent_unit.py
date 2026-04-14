from types import SimpleNamespace

from app.agents.legal_research.agent import LegalResearchAgent


def test_rerank_docs_prefers_substantive_section_over_preamble():
    agent = LegalResearchAgent()
    docs = [
        SimpleNamespace(
            page_content="Maharashtra Rent Control Act, 1999\nSection Preamble\nAn Act to unify, consolidate and amend the law relating to rent and eviction.",
            metadata={"act_name": "Maharashtra Rent Control Act, 1999", "section": "Preamble", "title": "Maharashtra Rent Control Act, 1999"},
        ),
        SimpleNamespace(
            page_content="Maharashtra Rent Control Act, 1999\nSection 16\nThe landlord shall be entitled to recover possession where the tenant is in arrears of rent and eviction is sought on statutory grounds.",
            metadata={"act_name": "Maharashtra Rent Control Act, 1999", "section": "16", "title": "Maharashtra Rent Control Act, 1999"},
        ),
    ]

    ranked = agent._rerank_docs(
        "What are the essential ingredients of a claim for eviction and recovery of arrears under the Maharashtra Rent Control Act, 1999?",
        docs,
        k=2,
    )

    assert ranked[0].metadata["section"] == "16"


def test_build_focus_queries_adds_act_and_section_queries():
    agent = LegalResearchAgent()

    queries = agent._build_focus_queries(
        "What are the grounds for eviction under Maharashtra Rent Control Act Section 16?"
    )

    assert "What are the grounds for eviction under Maharashtra Rent Control Act Section 16?" in queries
    assert "Maharashtra Rent Control Act, 1999" in queries
    assert "Maharashtra Rent Control Act, 1999 Section 16" in queries
