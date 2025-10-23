
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app import crud, schemas
from app.db.vector_db import get_vector_db

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def store_document(db: Session, doc_data: dict, content: str):
    """Stores the processed document in the database and vector store."""
    
    # 1. Store in PostgreSQL
    doc_create = schemas.DocumentCreate(
        title=doc_data.get("title", ""),
        content=content,
        owner_id=1  # Assuming a default owner for now
    )
    db_document = crud.document.create(db, obj_in=doc_create)

    # 2. Generate and store embeddings in ChromaDB
    vector_db = get_vector_db()
    collection = vector_db.get_or_create_collection("droitdraft_documents")
    
    embedding = model.encode(content).tolist()
    
    collection.add(
        ids=[str(db_document.id)],
        embeddings=[embedding],
        metadatas=[doc_data]
    )

    return db_document
