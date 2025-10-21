from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from app.utils.text_preprocessing import TextPreprocessor

class BM25Engine:
    """
    Implements the BM25 keyword-based search algorithm.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25 = None
        self.documents = []
        self.tokenized_documents = []
        self.text_preprocessor = TextPreprocessor()

    def index_documents(self, documents: List[Dict[str, Any]], document_id_key: str = "id", content_key: str = "content"):
        """
        Indexes a list of documents for BM25 search.

        Args:
            documents: A list of dictionaries, where each dictionary represents a document.
            document_id_key: The key in the document dictionary that holds the unique ID.
            content_key: The key in the document dictionary that holds the text content.
        """
        self.documents = documents
        self.tokenized_documents = [self.text_preprocessor.preprocess(doc[content_key]) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_documents, k1=self.k1, b=self.b)

    def search(self, query: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a BM25 search for the given query.

        Args:
            query: The search query string.
            top_n: The number of top results to return.

        Returns:
            A list of dictionaries, where each dictionary represents a matching document
            with its original content and a 'score' key.
        """
        if not self.bm25:
            return []

        tokenized_query = self.text_preprocessor.preprocess(query)
        doc_scores = self.bm25.get_scores(tokenized_query)

        # Pair scores with original documents and sort
        scored_documents = []
        for i, score in enumerate(doc_scores):
            if score > 0: # Filter out documents with 0 score
                scored_documents.append({"document": self.documents[i], "score": score})
        
        scored_documents.sort(key=lambda x: x["score"], reverse=True)

        return scored_documents[:top_n]
