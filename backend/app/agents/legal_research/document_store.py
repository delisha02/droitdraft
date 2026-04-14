import os
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document


def _coerce_metadata_value(value: Any) -> Optional[str | int | float | bool]:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _build_chroma_metadata(
    doc: Dict[str, Any],
    content_key: str = "content",
    metadata_exclude_keys: Optional[List[str]] = None,
) -> Dict[str, Any]:
    metadata_exclude_keys = metadata_exclude_keys or []
    metadata: Dict[str, Any] = {}

    nested_metadata = doc.get("metadata")
    if isinstance(nested_metadata, dict):
        for key, value in nested_metadata.items():
            if key in metadata_exclude_keys:
                continue
            coerced = _coerce_metadata_value(value)
            if coerced is not None:
                metadata[key] = coerced

    for key, value in doc.items():
        if key in {content_key, "metadata"} or key in metadata_exclude_keys:
            continue
        coerced = _coerce_metadata_value(value)
        if coerced is not None:
            metadata[key] = coerced

    return metadata

class DocumentStore:
    """
    A persistent document store using ChromaDB to store judgments/legal texts.
    """

    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "legal_judgments"):
        """
        Initialize the ChromaDB vector store.
        :param persist_directory: Directory to store the database.
        :param collection_name: Name of the collection to use.
        """
        # Ensure absolute path for persistence
        if not os.path.isabs(persist_directory):
            # perform relative to backend root or current working dir? 
            # Let's make it relative to the app root if possible, or just use what is passed.
            # Using absolute path based on backend directory usually safer.
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            persist_directory = os.path.join(base_dir, persist_directory)

        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize Embeddings (using local HuggingFaceEmbeddings model)
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError("langchain_huggingface is required for embeddings")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize Chroma
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_documents(self, documents: List[Dict[str, Any]], content_key: str = "content", metadata_exclude_keys: List[str] = None):
        """
        Adds a list of documents (dicts) to the store.
        Expects dicts with at least a content field (default 'content').
        Everything else is treated as metadata.
        """
        langchain_docs = []
        if metadata_exclude_keys is None:
            metadata_exclude_keys = []
            
        for doc in documents:
            content = doc.get(content_key)
            if not content:
                continue # Skip empty content

            metadata = _build_chroma_metadata(
                doc,
                content_key=content_key,
                metadata_exclude_keys=metadata_exclude_keys,
            )

            langchain_docs.append(Document(page_content=content, metadata=metadata))
        
        if langchain_docs:
            self.vector_store.add_documents(langchain_docs)

    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Performs a similarity search.
        """
        return self.vector_store.similarity_search(query, k=k)

    def get_retriever(self, search_kwargs: dict = None):
        """
        Returns a retriever interface for the vector store.
        """
        return self.vector_store.as_retriever(search_kwargs=search_kwargs or {})

    def delete_collection(self):
        """
        Deletes the entire collection. Use with caution.
        """
        self.vector_store.delete_collection()
