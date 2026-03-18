from unittest.mock import MagicMock, patch

from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document

from app.agents.legal_research.retrievers import get_hybrid_retriever


def test_get_hybrid_retriever_builds_dense_and_sparse_retrievers():
    docs = [
        Document(page_content="Section 138 NI Act applies.", metadata={"source": "s1"}),
        Document(page_content="Cheque dishonour procedure", metadata={"source": "s2"}),
    ]

    with patch("app.agents.legal_research.retrievers.SentenceTransformerEmbeddings") as MockEmbeddings, \
         patch("app.agents.legal_research.retrievers.Chroma") as MockChroma, \
         patch("app.agents.legal_research.retrievers.BM25Retriever") as MockBM25:

        mock_embeddings = MockEmbeddings.return_value
        mock_vectorstore = MockChroma.from_documents.return_value
        mock_vector_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_vector_retriever

        mock_bm25 = MagicMock()
        MockBM25.from_documents.return_value = mock_bm25

        retriever = get_hybrid_retriever(docs, k=3)

        assert isinstance(retriever, EnsembleRetriever)
        MockEmbeddings.assert_called_once()
        MockChroma.from_documents.assert_called_once_with(docs, mock_embeddings)
        MockBM25.from_documents.assert_called_once_with(docs)
        assert mock_bm25.k == 3
        assert len(retriever.retrievers) == 2
