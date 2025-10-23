
from sqlalchemy.orm import Session
from app.services import tasks

def store_article(db: Session, article_data: dict):
    """Stores the processed article in the database and triggers embedding and indexing."""
    
    # 1. Store in PostgreSQL
    doc_create = schemas.DocumentCreate(
        title=article_data.get("title", ""),
        content=article_data.get("content", ""),
        owner_id=1  # Assuming a default owner for now
    )
    db_document = crud.document.create(db, obj_in=doc_create)

    # 2. Trigger background task for embedding and indexing
    tasks.embed_and_index_task.delay(db_document.id, article_data["content"], article_data)

    return db_document
