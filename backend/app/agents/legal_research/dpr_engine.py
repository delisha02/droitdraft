from typing import List, Dict, Any, Optional
from app.utils.text_chunking import TextChunker
from app.agents.legal_research.passage_encoder import PassageEncoder
from app.agents.legal_research.query_encoder import QueryEncoder
from app.db.vector_db import get_vector_db
from chromadb.utils import embedding_functions
import numpy as np

class DPREngine:
    """
    Implements Dense Passage Retrieval (DPR) for semantic search.
    """

    def __init__(self, collection_name: str = "legal_passages"):
        self.text_chunker = TextChunker()
        self.passage_encoder = PassageEncoder()
        self.query_encoder = QueryEncoder()
        self.chroma_client = get_vector_db()
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """
        Gets an existing ChromaDB collection or creates a new one.
        """
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
        except Exception:
            # DefaultEmbeddingFunction is causing issues, so we explicitly set it to None
            # when creating the collection. Embeddings will be provided by InLegalBERT.
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="law-ai/InLegalBERT")
            )
        return collection

    def index_document(self, document_id: str, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Chunks a document, encodes passages, and stores them in ChromaDB.
        """
        chunks = self.text_chunker.chunk_text(text)
        if not chunks:
            return

        # Generate embeddings for all chunks in batches
        embeddings = self.passage_encoder.encode_passages(chunks)

        # Prepare metadata for each chunk
        metadatas = []
        ids = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {"document_id": document_id, "chunk_index": i, "text": chunk}
            if metadata:
                chunk_metadata.update(metadata)
            metadatas.append(chunk_metadata)
            ids.append(f"{document_id}_chunk_{i}")

        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic search using DPR.
        """
        if not query:
            return []

        query_embedding = self.query_encoder.encode_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 5, # Retrieve more results to aggregate by document
            include=['documents', 'metadatas', 'distances']
        )

        # Aggregate passage scores to document scores
        document_scores: Dict[str, Dict[str, Any]] = {}
        if results and results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                doc_id = results['metadatas'][0][i]['document_id']
                distance = results['distances'][0][i]
                passage_text = results['documents'][0][i]

                # Convert distance to similarity (cosine distance = 1 - cosine similarity)
                similarity = 1 - distance

                if doc_id not in document_scores:
                    document_scores[doc_id] = {
                        "document_id": doc_id,
                        "score": 0.0,
                        "passages": [],
                        "metadata": {k: v for k, v in results['metadatas'][0][i].items() if k not in ["document_id", "chunk_index", "text"]}
                    }
                
                # Sum similarities or take max similarity for document score
                document_scores[doc_id]["score"] += similarity
                document_scores[doc_id]["passages"].append({"text": passage_text, "score": similarity, "chunk_index": results['metadatas'][0][i]['chunk_index']})

        # Sort documents by aggregated score and return top_k
        sorted_documents = sorted(document_scores.values(), key=lambda x: x["score"], reverse=True)
        return sorted_documents[:top_k]
