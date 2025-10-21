from typing import List, Dict, Any, Optional
from app.agents.legal_research.bm25_engine import BM25Engine
from app.utils.text_preprocessing import TextPreprocessor

class DocumentIndexer:
    """
    Manages the indexing and retrieval of legal documents using BM25.
    """

    def __init__(self, bm25_k1: float = 1.5, bm25_b: float = 0.75):
        self.bm25_engine = BM25Engine(k1=bm25_k1, b=bm25_b)
        self.text_preprocessor = TextPreprocessor()
        self.documents_store: Dict[str, Dict[str, Any]] = {}
        self._rebuild_index_needed = False

    def _preprocess_document(self, document_content: str) -> List[str]:
        """
        Preprocesses document content for indexing.
        """
        return self.text_preprocessor.preprocess(document_content)

    def add_document(self, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Adds a new document to the index.
        """
        if document_id in self.documents_store:
            raise ValueError(f"Document with ID {document_id} already exists.")

        preprocessed_content = self._preprocess_document(content)
        self.documents_store[document_id] = {
            "id": document_id,
            "content": content,
            "preprocessed_content": " ".join(preprocessed_content), # Store as string for BM25Engine
            "metadata": metadata if metadata is not None else {}
        }
        self._rebuild_index_needed = True

    def update_document(self, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Updates an existing document in the index.
        """
        if document_id not in self.documents_store:
            raise ValueError(f"Document with ID {document_id} not found.")

        preprocessed_content = self._preprocess_document(content)
        self.documents_store[document_id].update({
            "content": content,
            "preprocessed_content": " ".join(preprocessed_content),
            "metadata": metadata if metadata is not None else self.documents_store[document_id]["metadata"]
        })
        self._rebuild_index_needed = True

    def delete_document(self, document_id: str):
        """
        Deletes a document from the index.
        """
        if document_id not in self.documents_store:
            raise ValueError(f"Document with ID {document_id} not found.")
        del self.documents_store[document_id]
        self._rebuild_index_needed = True

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a document by its ID.
        """
        return self.documents_store.get(document_id)

    def _rebuild_bm25_index(self):
        """
        Rebuilds the BM25 index from the current documents store.
        """
        if self.documents_store and self._rebuild_index_needed:
            documents_for_bm25 = list(self.documents_store.values())
            self.bm25_engine.index_documents(documents_for_bm25, content_key="preprocessed_content")
            self._rebuild_index_needed = False
        elif not self.documents_store:
            self.bm25_engine.bm25 = None # Clear BM25 index if no documents

    def search_documents(self, query: str, top_n: int = 5, 
                         jurisdiction: Optional[str] = None, 
                         start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Searches documents using BM25, with optional metadata filtering.
        """
        self._rebuild_bm25_index() # Ensure index is up-to-date

        if not self.bm25_engine.bm25:
            return []

        preprocessed_query = " ".join(self.text_preprocessor.preprocess(query))
        bm25_results = self.bm25_engine.search(preprocessed_query, top_n=len(self.documents_store)) # Get scores for all docs

        filtered_results = []
        for result in bm25_results:
            doc = result["document"]
            metadata = doc["metadata"]

            # Apply jurisdiction filter
            if jurisdiction and metadata.get("jurisdiction") != jurisdiction:
                continue

            # Apply date range filter
            if start_date and metadata.get("date") and metadata["date"] < start_date:
                continue
            if end_date and metadata.get("date") and metadata["date"] > end_date:
                continue
            
            filtered_results.append(result)

        # Re-sort and return top_n after filtering
        filtered_results.sort(key=lambda x: x["score"], reverse=True)
        return filtered_results[:top_n]
