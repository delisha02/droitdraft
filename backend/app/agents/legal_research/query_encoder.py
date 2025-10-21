from typing import List
import torch
from sentence_transformers import SentenceTransformer
from functools import lru_cache

class QueryEncoder:
    """
    Encodes user queries into dense vector embeddings using InLegalBERT.
    """

    def __init__(self, model_name: str = "law-ai/InLegalBERT", device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_name)

    @lru_cache(maxsize=1) # Cache the model loading
    def _load_model(self, model_name: str) -> SentenceTransformer:
        """
        Loads the SentenceTransformer model.
        """
        print(f"Loading SentenceTransformer model for queries: {model_name} on {self.device}")
        model = SentenceTransformer(model_name, device=self.device)
        return model

    @lru_cache(maxsize=128) # Cache frequently used query embeddings
    def encode_query(self, query: str) -> List[float]:
        """
        Generates an embedding for a single query.
        """
        if not query:
            return []
        
        embedding = self.model.encode(query, show_progress_bar=False)
        return embedding.tolist()

    def encode_queries(self, queries: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generates embeddings for a list of queries.
        """
        if not queries:
            return []
        
        embeddings = self.model.encode(queries, batch_size=batch_size, show_progress_bar=False)
        return embeddings.tolist()
