
from typing import List

def recursive_chunking(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Splits a long text into chunks of a specified size with overlap."""
    import logging
    logger = logging.getLogger(__name__)
    if len(text) <= chunk_size:
        logger.info(f"[Step 2] Text shorter than chunk size. Returning as single chunk.")
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    logger.info(f"[Step 2] Recursive chunking produced {len(chunks)} chunks. Example chunk: {chunks[0][:200]}...")
    return chunks
    return chunks
