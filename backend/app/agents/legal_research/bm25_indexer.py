
from typing import List, Dict, Any, Optional
from .document_store import DocumentStore
from .bm25_engine import BM25Engine

class BM25Indexer:
    """
    Manages the BM25 index.
    """

    def __init__(self, document_store: DocumentStore, index_path: str, k1: float = 1.5, b: float = 0.75):
        self.document_store = document_store
        self.index_path = index_path
        self.bm25_engine = BM25Engine(document_store, k1=k1, b=b)
        self._load_index()
        # Ensure index is built if not loaded from file
        if self.bm25_engine.bm25 is None:
            self.bm25_engine._build_index()

    def _load_index(self):
        """
        Loads the BM25 index from disk if it exists.
        """
        print(f"BM25Indexer - _load_index: Attempting to load index from {self.index_path}")
        try:
            self.bm25_engine.load_index(self.index_path)
            print("BM25Indexer - _load_index: Index loaded successfully.")
        except FileNotFoundError:
            print("BM25Indexer - _load_index: Index file not found, rebuilding index.")
            self.rebuild_index()

    def rebuild_index(self):
        """
        Rebuilds the BM25 index and saves it to disk.
        """
        print("BM25Indexer - rebuild_index: Rebuilding index...")
        self.bm25_engine._build_index()
        self.bm25_engine.save_index(self.index_path)
        print("BM25Indexer - rebuild_index: Index rebuilt and saved.")
    def search(self, query: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a BM25 search.
        """
        return self.bm25_engine.search(query, top_n=top_n)
