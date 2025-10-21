from typing import List
import torch
from sentence_transformers import SentenceTransformer
from functools import lru_cache

class PassageEncoder:
    """
    Encodes legal passages into dense vector embeddings using InLegalBERT.
    """

    def __init__(self, model_name: str = "law-ai/InLegalBERT", device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_name)

    @lru_cache(maxsize=1) # Cache the model loading
    def _load_model(self, model_name: str) -> SentenceTransformer:
        """
        Loads the SentenceTransformer model.
        """
        print(f"Loading SentenceTransformer model: {model_name} on {self.device}")
        model = SentenceTransformer(model_name, device=self.device)
        return model

    def encode_passages(self, passages: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generates embeddings for a list of passages.
        """
        if not passages:
            return []
        
        embeddings = self.model.encode(passages, batch_size=batch_size, show_progress_bar=False)
        return embeddings.tolist()
