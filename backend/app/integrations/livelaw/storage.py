
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app import crud, schemas
from app.db.vector_db import get_vector_db

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def store_article(db: Session, article_data: dict):
    """Stores the processed article in the database and vector store."""
    
    # 1. Store in PostgreSQL
    doc_create = schemas.DocumentCreate(
        title=article_data.get("title", ""),
        content=article_data.get("content", ""),
        owner_id=1  # Assuming a default owner for now
    )
    db_document = crud.document.create(db, obj_in=doc_create)

    # 2. Generate and store embeddings in ChromaDB
    vector_db = get_vector_db()
    collection = vector_db.get_or_create_collection("droitdraft_livelaw")
    
    embedding = model.encode(article_data["content"]).tolist()
    
    # Prepare metadata for ChromaDB
    metadata = {
        "title": article_data.get("title"),
        "publication_date": str(article_data.get("publication_date")),
        "relevance_score": article_data.get("relevance_score"),
        "fingerprint": article_data.get("fingerprint"),
        "case_references": ",".join(article_data.get("case_references", []))
    }

    collection.add(
        ids=[str(db_document.id)],
        embeddings=[embedding],
        metadatas=[metadata]
    )

    return db_document
