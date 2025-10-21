
from typing import List, Dict, Any, Optional

class DocumentStore:
    """
    A simple in-memory document store.
    """

    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}

    def add_documents(self, documents: List[Dict[str, Any]], document_id_key: str = "id"):
        """
        Adds a list of documents to the store.
        """
        for doc in documents:
            doc_id = doc.get(document_id_key)
            if doc_id:
                self.documents[doc_id] = doc

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a document by its ID.
        """
        return self.documents.get(document_id)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Retrieves all documents from the store.
        """
        return list(self.documents.values())

    def delete_document(self, document_id: str):
        """
        Deletes a document from the store.
        """
        if document_id in self.documents:
            del self.documents[document_id]
