

from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = HuggingFaceEmbeddings(model_name=model_name)

    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of text chunks."""
        # HuggingFaceEmbeddings expects a list of strings and returns a list of embeddings
        return self.model.embed_documents(chunks)
