from langchain_community.retrievers.bm25 import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings


def get_persistent_retriever(persist_directory: str = "chroma_db", collection_name: str = "legal_judgments", k: int = 5):
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
        persist_directory=persist_directory
    )
    
    return vectorstore.as_retriever(search_kwargs={"k": k})

