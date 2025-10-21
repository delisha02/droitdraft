
import pytest
from app.agents.legal_research.dpr_engine import DPREngine

@pytest.fixture(scope="module")
def dpr_engine():
    """Fixture for DPREngine."""
    return DPREngine(collection_name="test_legal_passages")

@pytest.fixture(autouse=True)
def cleanup_collection(dpr_engine):
    """Clean up the collection after tests."""
    yield
    try:
        dpr_engine.chroma_client.delete_collection(name="test_legal_passages")
    except Exception as e:
        print(f"Error cleaning up collection: {e}")

def test_index_and_search(dpr_engine):
    """Test indexing a document and performing a semantic search."""
    doc_id = "test_doc_1"
    text = "This is a test document about contract law."
    metadata = {"category": "test"}

    dpr_engine.index_document(doc_id, text, metadata)

    # Allow some time for indexing to complete
    import time
    time.sleep(1)

    search_results = dpr_engine.search("contract law", top_k=1)

    assert len(search_results) == 1
    assert search_results[0]["document_id"] == doc_id
    assert "passages" in search_results[0]
    assert len(search_results[0]["passages"]) > 0
    assert search_results[0]["passages"][0]["text"] in text
