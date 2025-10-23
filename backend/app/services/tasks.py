
from app.celery_app import celery_app
from app.services.corpus_ingestion import CorpusIngestionService
from app.api import deps

@celery_app.task
def ingest_indian_kanoon_task(doc_id: str):
    """Celery task to ingest a document from Indian Kanoon."""
    db = next(deps.get_db())
    ingestion_service = CorpusIngestionService(db)
    ingestion_service.ingest_from_indian_kanoon(doc_id)

@celery_app.task
def ingest_livelaw_task():
    """Celery task to ingest latest news from LiveLaw."""
    db = next(deps.get_db())
    ingestion_service = CorpusIngestionService(db)
    ingestion_service.ingest_from_livelaw()
