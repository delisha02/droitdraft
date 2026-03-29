import os
from typing import List

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_classic.retrievers import EnsembleRetriever


class HybridLegalRetriever:
    """
    Hybrid retriever that combines dense Chroma retrieval with BM25 sparse retrieval
    using Reciprocal Rank Fusion via LangChain's EnsembleRetriever.

    BM25 index is built from the persisted Chroma collection to avoid duplicate
    ingestion pipelines.
    """

    def __init__(self, vector_retriever: BaseRetriever, bm25_retriever: BaseRetriever):
        # Favor dense retrieval slightly while still benefiting from keyword matches.
        self.ensemble = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.65, 0.35],
        )

    def invoke(self, query: str):
        return self.ensemble.invoke(query)


def _build_sparse_retriever_from_chroma(vectorstore: Chroma, k: int) -> BaseRetriever:
    """
    Build BM25 retriever from all documents already persisted in Chroma.
    Falls back to an empty retriever-safe list when no docs exist.
    """
    collection_payload = vectorstore.get(include=["documents", "metadatas"])
    documents: List[str] = collection_payload.get("documents") or []
    metadatas: List[dict] = collection_payload.get("metadatas") or []

    bm25_docs: List[Document] = []
    for idx, content in enumerate(documents):
        if not content:
            continue
        metadata = metadatas[idx] if idx < len(metadatas) and metadatas[idx] else {}
        bm25_docs.append(Document(page_content=content, metadata=metadata))

    if not bm25_docs:
        # BM25Retriever requires at least one document.
        bm25_docs = [Document(page_content="", metadata={"source": "empty"})]

    bm25 = BM25Retriever.from_documents(bm25_docs)
    bm25.k = k
    return bm25


def get_persistent_retriever(
    persist_directory: str = "chroma_db",
    collection_name: str = "legal_judgments",
    k: int = 5,
):
    """
    Returns a hybrid retriever connected to persistent ChromaDB.
    Combines semantic retrieval (dense vectors) with lexical retrieval (BM25).
    """
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    if not os.path.isabs(persist_directory):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        persist_directory = os.path.join(base_dir, persist_directory)

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    bm25_retriever = _build_sparse_retriever_from_chroma(vectorstore=vectorstore, k=k)

    return HybridLegalRetriever(
        vector_retriever=dense_retriever,
        bm25_retriever=bm25_retriever,
    )
