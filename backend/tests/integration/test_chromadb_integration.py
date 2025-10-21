import pytest
import chromadb
from app.core.config import settings

@pytest.fixture(scope="module")
def live_chroma_client():
    """
    Fixture to provide a live ChromaDB client.
    Requires a running ChromaDB instance.
    """
    try:
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        # Ping the client to ensure connection
        client.heartbeat()
        yield client
    except Exception as e:
        pytest.fail(f"Could not connect to live ChromaDB at {settings.CHROMA_HOST}:{settings.CHROMA_PORT}. "
                     f"Please ensure the ChromaDB container is running and accessible. Error: {e}")

def test_live_chromadb_connection(live_chroma_client):
    """
    Tests basic connection and operations with a live ChromaDB instance.
    """
    collection_name = "test_collection_live"

    # Clean up any existing collection from previous runs
    try:
        live_chroma_client.delete_collection(name=collection_name)
    except Exception:
        pass # Collection might not exist

    # Create a collection
    collection = live_chroma_client.create_collection(name=collection_name)
    assert collection.name == collection_name

    # Add some data
    collection.add(
        documents=["This is a test document", "This is another document"],
        metadatas=[{"source": "test"}, {"source": "test"}],
        ids=["doc1", "doc2"]
    )
    assert collection.count() == 2

    # Query data
    results = collection.query(
        query_texts=["test document"],
        n_results=1
    )
    assert len(results['ids'][0]) == 1
    assert "doc1" in results['ids'][0]

    # Delete the collection
    live_chroma_client.delete_collection(name=collection_name)
    assert collection_name not in [c.name for c in live_chroma_client.list_collections()]
