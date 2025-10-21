import pytest
from unittest.mock import MagicMock

def test_chromadb_connection(mocker):
    """
    Tests the ChromaDB connection logic by mocking the chromadb client.
    """
    # Mock the chromadb.HttpClient
    mock_client = MagicMock()
    mocker.patch('chromadb.HttpClient', return_value=mock_client)

    # Since the client is created on module import, we need to reload the module
    import importlib
    from app.db import vector_db
    importlib.reload(vector_db)

    # Get the client from the reloaded module
    client = vector_db.get_vector_db()

    # Assert that the client is the mocked client
    assert client == mock_client

    # You can also add assertions to check if the client's methods are called
    collection_name = "test_collection"
    client.create_collection(name=collection_name)
    mock_client.create_collection.assert_called_with(name=collection_name)

    client.delete_collection(name=collection_name)
    mock_client.delete_collection.assert_called_with(name=collection_name)
