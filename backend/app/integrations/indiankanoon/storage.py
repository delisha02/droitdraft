
from sqlalchemy.orm import Session
from app.services import tasks

def store_document(db: Session, doc_data: dict, content: str):
    """Stores the processed document in the database and triggers embedding and indexing."""
    
    # 1. Store in PostgreSQL
    doc_create = schemas.DocumentCreate(
        title=doc_data.get("title", ""),
        content=content,
        owner_id=1  # Assuming a default owner for now
    )
    db_document = crud.document.create(db, obj_in=doc_create)

    # 2. Trigger background task for embedding and indexing
    tasks.embed_and_index_task.delay(db_document.id, content, doc_data)

    return db_document
