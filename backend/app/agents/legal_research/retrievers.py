from langchain_community.retrievers.bm25 import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

def get_hybrid_retriever(documents: List[Document]):
    # Initialize BM25Retriever
    bm25_retriever = BM25Retriever.from_documents(documents)

    # Initialize your vector store retriever here (e.g., Chroma, FAISS)
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(documents, embeddings)
    vector_retriever = vectorstore.as_retriever()

    # Initialize EnsembleRetriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever], weights=[0.5, 0.5]
    )
    return ensemble_retriever
