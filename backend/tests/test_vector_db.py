import pytest
from app.db.vector_db import get_vector_db

def test_chromadb_connection():
    """
    Tests the connection to ChromaDB by creating and deleting a collection.
    """
    client = get_vector_db()
    
    # 1. Heartbeat check
    try:
        heartbeat = client.heartbeat()
        assert isinstance(heartbeat, int)
    except Exception as e:
        pytest.fail(f"ChromaDB heartbeat failed: {e}")

    # 2. Create a test collection
    collection_name = "test_collection"
    try:
        collection = client.create_collection(name=collection_name)
        assert collection.name == collection_name
    except Exception as e:
        # If the collection already exists, delete it and try again.
        # This can happen if a previous test run failed.
        try:
            client.delete_collection(name=collection_name)
            collection = client.create_collection(name=collection_name)
            assert collection.name == collection_name
        except Exception as e2:
            pytest.fail(f"ChromaDB create_collection failed even after cleanup: {e2}")

    # 3. Delete the test collection
    try:
        client.delete_collection(name=collection_name)
        # Verify the collection is deleted by trying to get it
        with pytest.raises(Exception):
            client.get_collection(name=collection_name)
    except Exception as e:
        pytest.fail(f"ChromaDB delete_collection failed: {e}")
