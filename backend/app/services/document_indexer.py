
from typing import List, Dict, Any

from app.db.vector_db import get_vector_db
from app.services.embedding_generator import EmbeddingGenerator
from app.utils.chunking_strategies import recursive_chunking

class DocumentIndexer:
    def __init__(self, collection_name: str = "droitdraft_documents"):
        self.vector_db = get_vector_db()
        self.collection = self.vector_db.get_or_create_collection(collection_name)
        self.embedding_generator = EmbeddingGenerator()

    def index_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Chunks, generates embeddings for, and indexes a document."""
        
        # 1. Chunk the document
        chunks = recursive_chunking(content)
        
        # 2. Generate embeddings for the chunks
        embeddings = self.embedding_generator.generate_embeddings(chunks)
        
        # 3. Prepare data for ChromaDB
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [metadata] * len(chunks)
        
        # 4. Index the chunks and embeddings
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
