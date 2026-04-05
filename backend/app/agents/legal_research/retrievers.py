try:
    from langchain_community.retrievers.bm25 import BM25Retriever  # type: ignore
except Exception:
    class BM25Retriever:  # type: ignore[misc]
        @classmethod
        def from_documents(cls, _documents):
            raise ImportError("langchain_community is required for BM25Retriever")


try:
    from langchain_core.documents import Document  # type: ignore
except Exception:
    from typing import Any as Document  # type: ignore

from typing import List

try:
    from langchain_community.vectorstores import Chroma  # type: ignore
except Exception:
    class Chroma:  # type: ignore[misc]
        @classmethod
        def from_documents(cls, _documents, _embeddings):
            raise ImportError("langchain_community is required for Chroma")

        def __init__(self, *args, **kwargs):
            raise ImportError("langchain_community is required for Chroma")


try:
    from langchain_community.embeddings import SentenceTransformerEmbeddings  # type: ignore
except Exception:
    class SentenceTransformerEmbeddings:  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            raise ImportError("langchain_community is required for embeddings")


try:
    from langchain_classic.retrievers.ensemble import EnsembleRetriever  # type: ignore
except Exception:
    class EnsembleRetriever:  # type: ignore[misc]
        """
        Lightweight fallback ensemble retriever used when langchain-classic
        is unavailable in the runtime environment.
        """
        def __init__(self, retrievers: list, weights: list[float] | None = None):
            self.retrievers = retrievers
            self.weights = weights or [1.0 for _ in retrievers]

        def invoke(self, query: str, *args, **kwargs):
            seen = set()
            merged = []
            for retriever in self.retrievers:
                for doc in retriever.invoke(query):
                    doc_key = (getattr(doc, "page_content", None), str(getattr(doc, "metadata", {})))
                    if doc_key not in seen:
                        seen.add(doc_key)
                        merged.append(doc)
            return merged


def get_hybrid_retriever(
    documents: List[Document],
    embedding_model: str = "all-MiniLM-L6-v2",
    k: int = 5,
    keyword_weight: float = 0.6,
    semantic_weight: float = 0.4,
) -> EnsembleRetriever:
    """
    Builds an in-memory hybrid retriever using dense + sparse retrieval.

    This is primarily used for testing and local experimentation where a
    list of LangChain `Document` objects is already available.
    """
    embeddings = SentenceTransformerEmbeddings(model_name=embedding_model)

    # Dense retriever via vector store
    vectorstore = Chroma.from_documents(documents, embeddings)
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # Sparse retriever via BM25
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = k

    # Normalize and clamp weights to keep them valid
    keyword_weight = max(float(keyword_weight), 0.0)
    semantic_weight = max(float(semantic_weight), 0.0)
    total_weight = keyword_weight + semantic_weight
    if total_weight <= 0:
        norm_keyword_weight, norm_semantic_weight = 0.5, 0.5
    else:
        norm_keyword_weight = keyword_weight / total_weight
        norm_semantic_weight = semantic_weight / total_weight

    # Fuse results from both retrievers
    return EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[norm_keyword_weight, norm_semantic_weight],
    )


def get_persistent_retriever(
    persist_directory: str = "chroma_db",
    collection_name: str = "legal_judgments",
    k: int = 5,
):
    """
    Returns a retriever connected to the persistent ChromaDB.
    """
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Initialize connection to existing DB
    # Note: We need to ensure we point to the same directory as DocumentStore
    import os
    if not os.path.isabs(persist_directory):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        persist_directory = os.path.join(base_dir, persist_directory)

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})
