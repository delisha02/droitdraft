
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app import crud

from app.api import deps
from app.services.corpus_ingestion import CorpusIngestionService
from app.services.ingestion_monitor import ingestion_monitor
from app.services import tasks

router = APIRouter()


@router.post("/ingest/indiankanoon/{doc_id}", status_code=202)
async def ingest_indian_kanoon(doc_id: str):
    """Trigger the ingestion of a document from Indian Kanoon."""
    tasks.ingest_indian_kanoon_task.delay(doc_id)
    return {"message": f"Ingestion of Indian Kanoon document {doc_id} triggered."}


@router.post("/ingest/livelaw", status_code=202)
async def ingest_livelaw():
    """Trigger the ingestion of latest news from LiveLaw."""
    tasks.ingest_livelaw_task.delay()
    return {"message": "Ingestion of LiveLaw latest news triggered."}


@router.post("/ingest/upload", status_code=202)
async def ingest_upload(
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...)
):
    """Ingest a document from a file upload."""
    content = await file.read()
    ingestion_service = CorpusIngestionService(db)
    await ingestion_service.ingest_from_upload(content.decode("utf-8"), {"title": file.filename})
    return {"message": f"File {file.filename} ingested successfully."}


@router.get("/ingest/stats")
async def get_ingestion_stats():
    """Get ingestion statistics."""
    return ingestion_monitor.get_stats()


@router.post("/index/{doc_id}", status_code=202)
async def index_document(
    doc_id: int,
    db: Session = Depends(deps.get_db)
):
    """Trigger the embedding and indexing of a document."""
    document = crud.document.get(db, id=doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    tasks.embed_and_index_task.delay(document.id, document.content, {"title": document.title})
    return {"message": f"Indexing of document {doc_id} triggered."}
