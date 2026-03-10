from typing import List

class TextChunker:
    """
    Splits long legal documents into passages (chunks) for encoding.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits a given text into overlapping chunks.
        A simple token-based chunking for now. More sophisticated methods
        might consider sentence boundaries or legal section structures.
        """
        import logging
        logger = logging.getLogger(__name__)
        words = text.split()
        chunks = []
        
        if not words:
            logger.info("[Step 2] No words to chunk.")
            return []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk))

        logger.info(f"[Step 2] Chunked text into {len(chunks)} chunks. Example chunk: {chunks[0][:200]}..." if chunks else "[Step 2] No chunks created.")
        return chunks
