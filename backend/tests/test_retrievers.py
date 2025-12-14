
import pytest
from unittest.mock import MagicMock, patch
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.runnables import Runnable
from app.agents.legal_research.retrievers import get_hybrid_retriever

@pytest.fixture
def sample_documents():
    return [
        Document(page_content="The quick brown fox jumps over the lazy dog.", metadata={"source": "doc1"}),
        Document(page_content="A fast animal is a fox.", metadata={"source": "doc2"}),
        Document(page_content="The dog is very lazy and sleeps all day.", metadata={"source": "doc3"}),
    ]

@patch('app.agents.legal_research.retrievers.BM25Retriever')
@patch('app.agents.legal_research.retrievers.Chroma')
@patch('app.agents.legal_research.retrievers.SentenceTransformerEmbeddings')
def test_get_hybrid_retriever(MockSentenceTransformerEmbeddings, MockChroma, MockBM25Retriever, sample_documents):
    # Arrange
    mock_embeddings = MockSentenceTransformerEmbeddings.return_value

    # Setup mock for Chroma vector retriever
    mock_vector_retriever = MagicMock(spec=Runnable)
    mock_vectorstore = MockChroma.from_documents.return_value
    mock_vectorstore.as_retriever.return_value = mock_vector_retriever

    # Setup mock for BM25 retriever
    mock_bm25_retriever = MagicMock(spec=Runnable)
    MockBM25Retriever.from_documents.return_value = mock_bm25_retriever

    # Act
    retriever = get_hybrid_retriever(sample_documents)

    # Assert
    assert isinstance(retriever, EnsembleRetriever)
    assert len(retriever.retrievers) == 2

    # Check that the underlying retrievers were created correctly
    MockChroma.from_documents.assert_called_once_with(sample_documents, mock_embeddings)
    MockBM25Retriever.from_documents.assert_called_once_with(sample_documents)

    # Test invoking the retriever
    query = "lazy fox"
    retriever.invoke(query)

    # Assert that the invoke methods of both mocked retrievers were called
    mock_bm25_retriever.invoke.assert_called_once()
    mock_vector_retriever.invoke.assert_called_once()
