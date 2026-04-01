from typing import List, Optional

from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.agents.legal_research.retrievers import (
    get_hybrid_retriever,
    get_persistent_retriever,
)


class RetrievalService:
    """
    Centralized retrieval facade used by research and generation pipelines.

    This keeps retriever construction in one place so we can evolve retrieval
    strategy (dense-only vs hybrid) without touching every caller.
    """

    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "legal_judgments"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name

    def get_persistent_retriever(self, k: int = 5) -> BaseRetriever:
        return get_persistent_retriever(
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            k=k,
        )

    def get_hybrid_retriever(
        self,
        documents: List[Document],
        embedding_model: str = "all-MiniLM-L6-v2",
        k: int = 5,
    ) -> EnsembleRetriever:
        return get_hybrid_retriever(
            documents=documents,
            embedding_model=embedding_model,
            k=k,
        )

