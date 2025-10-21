import pickle
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from app.utils.text_preprocessing import TextPreprocessor
from .document_store import DocumentStore

class BM25Engine:
    """
    Implements the BM25 keyword-based search algorithm.
    """

    def __init__(self, document_store: DocumentStore, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.document_store = document_store
        self.text_preprocessor = TextPreprocessor()
        self.bm25 = None
        self._build_index()

    def _build_index(self):
        """
        Builds the BM25 index from the documents in the document store.
        """
        documents = self.document_store.get_all_documents()
        if documents:
            tokenized_documents = [self.text_preprocessor.preprocess(doc["content"]) for doc in documents]
            self.bm25 = BM25Okapi(tokenized_documents, k1=self.k1, b=self.b)
        else:
            self.bm25 = None

    def search(self, query: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a BM25 search for the given query.
        """
        if not self.bm25:
            return []

        tokenized_query = self.text_preprocessor.preprocess(query)
        doc_scores = self.bm25.get_scores(tokenized_query)

        documents = self.document_store.get_all_documents()
        scored_documents = []
        for i, score in enumerate(doc_scores):
            if score > 0:
                scored_documents.append({"document": documents[i], "score": score})
        
        scored_documents.sort(key=lambda x: x["score"], reverse=True)

        return scored_documents[:top_n]

    def save_index(self, path: str):
        """
        Saves the BM25 index to a file.
        """
        with open(path, "wb") as f:
            pickle.dump(self.bm25, f)

    def load_index(self, path: str):
        """
        Loads the BM25 index from a file.
        """
        with open(path, "rb") as f:
            self.bm25 = pickle.load(f)
