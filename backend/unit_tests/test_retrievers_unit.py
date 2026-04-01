from unittest.mock import MagicMock, patch
import importlib.util
from pathlib import Path

_RETRIEVERS_PATH = Path(__file__).resolve().parents[1] / "app" / "agents" / "legal_research" / "retrievers.py"
_SPEC = importlib.util.spec_from_file_location("retrievers_under_test", _RETRIEVERS_PATH)
_MODULE = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_MODULE)
get_hybrid_retriever = _MODULE.get_hybrid_retriever


def test_get_hybrid_retriever_builds_dense_and_sparse_retrievers():
    docs = [
        {"page_content": "Section 138 NI Act applies.", "metadata": {"source": "s1"}},
        {"page_content": "Cheque dishonour procedure", "metadata": {"source": "s2"}},
    ]

    with patch.object(_MODULE, "SentenceTransformerEmbeddings") as MockEmbeddings, \
         patch.object(_MODULE, "Chroma") as MockChroma, \
         patch.object(_MODULE, "BM25Retriever") as MockBM25:

        mock_embeddings = MockEmbeddings.return_value
        mock_vectorstore = MockChroma.from_documents.return_value
        mock_vector_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_vector_retriever

        mock_bm25 = MagicMock()
        MockBM25.from_documents.return_value = mock_bm25

        retriever = get_hybrid_retriever(docs, k=3)

        assert hasattr(retriever, "retrievers")
        MockEmbeddings.assert_called_once()
        MockChroma.from_documents.assert_called_once_with(docs, mock_embeddings)
        MockBM25.from_documents.assert_called_once_with(docs)
        assert mock_bm25.k == 3
        assert len(retriever.retrievers) == 2
        assert retriever.weights == [0.5, 0.5]


def test_ensemble_retriever_contract_has_invoke():
    docs = [
        {"page_content": "A", "metadata": {"id": 1}},
    ]

    with patch.object(_MODULE, "SentenceTransformerEmbeddings"), \
         patch.object(_MODULE, "Chroma") as MockChroma, \
         patch.object(_MODULE, "BM25Retriever") as MockBM25:

        mock_vectorstore = MockChroma.from_documents.return_value
        mock_vector = MagicMock()
        mock_vector.invoke.return_value = docs
        mock_vectorstore.as_retriever.return_value = mock_vector

        mock_bm25 = MagicMock()
        mock_bm25.invoke.return_value = docs
        MockBM25.from_documents.return_value = mock_bm25

        retriever = get_hybrid_retriever(docs, k=1)
        result = retriever.invoke("query")
        assert isinstance(result, list)
