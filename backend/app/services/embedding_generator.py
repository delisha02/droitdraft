
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of text chunks."""
        return self.model.encode(chunks).tolist()
