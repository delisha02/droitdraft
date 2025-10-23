
from typing import List

def recursive_chunking(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Splits a long text into chunks of a specified size with overlap."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
        
    return chunks
