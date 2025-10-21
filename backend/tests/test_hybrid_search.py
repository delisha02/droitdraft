
import pytest
from unittest.mock import MagicMock
from app.agents.legal_research.hybrid_search import HybridSearch
from app.agents.legal_research.bm25_engine import BM25Engine
from app.agents.legal_research.dpr_engine import DPREngine
from app.agents.legal_research.document_store import DocumentStore

@pytest.fixture
def mock_bm25_engine():
    engine = MagicMock(spec=BM25Engine)
    engine.search.return_value = [
        {"document": {"id": "doc1", "metadata": {"jurisdiction": "US", "date": "2023-01-01"}}, "score": 0.9},
        {"document": {"id": "doc2", "metadata": {"jurisdiction": "UK", "date": "2022-01-01"}}, "score": 0.8},
    ]
    return engine

@pytest.fixture
def mock_dpr_engine():
    engine = MagicMock(spec=DPREngine)
    engine.search.return_value = [
        {"document": {"id": "doc2", "metadata": {"jurisdiction": "UK", "date": "2022-01-01"}}, "score": 0.95},
        {"document": {"id": "doc3", "metadata": {"jurisdiction": "US", "date": "2023-05-01"}}, "score": 0.85},
    ]
    return engine

@pytest.fixture
def mock_document_store():
    store = MagicMock(spec=DocumentStore)
    store.get_document.side_effect = lambda doc_id: {"id": doc_id, "content": f"Content of {doc_id}", "metadata": {"jurisdiction": "US", "date": "2023-01-01"}}
    return store

@pytest.fixture
def hybrid_search_engine(mock_bm25_engine, mock_dpr_engine, mock_document_store):
    return HybridSearch(search_engines=[mock_bm25_engine, mock_dpr_engine], document_store=mock_document_store)

def test_hybrid_search_initialization(hybrid_search_engine):
    assert hybrid_search_engine is not None

def test_hybrid_search_reciprocal_rank_fusion(hybrid_search_engine):
    hybrid_search_engine.config["fusion_algorithm"] = "reciprocal_rank_fusion"
    results = hybrid_search_engine.search("some query")
    assert len(results) > 0
    # doc2 should be ranked higher due to RRF
    assert results[0]["document"]["id"] == "doc2"

def test_hybrid_search_weighted_linear_combination(hybrid_search_engine):
    hybrid_search_engine.config["fusion_algorithm"] = "weighted_linear_combination"
    results = hybrid_search_engine.search("some query")
    assert len(results) > 0

def test_hybrid_search_deduplication(hybrid_search_engine):
    results = hybrid_search_engine.search("some query")
    doc_ids = [res["document"]["id"] for res in results]
    assert len(doc_ids) == len(set(doc_ids))

def test_hybrid_search_reranking(hybrid_search_engine):
    hybrid_search_engine.config["boost_factors"] = {
        "jurisdiction": "UK",
        "jurisdiction_boost": 2.0,
    }
    results = hybrid_search_engine.search("some query")
    # doc2 is from UK and should be boosted
    assert results[0]["document"]["id"] == "doc2"
