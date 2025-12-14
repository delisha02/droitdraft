# from app.celery_app import celery_app
# # from app.services.corpus_ingestion import CorpusIngestionService # Moved inside functions
# from app.api import deps

# # @celery_app.task
# # def ingest_indian_kanoon_task(doc_id: str):
# #     """Celery task to ingest a document from Indian Kanoon."""
# #     from app.services.corpus_ingestion import CorpusIngestionService # Moved here
# #     db = next(deps.get_db())
# #     ingestion_service = CorpusIngestionService(db)
# #     ingestion_service.ingest_from_indian_kanoon(doc_id)

# # @celery_app.task
# # def ingest_livelaw_task():
# #     """Celery task to ingest latest news from LiveLaw."""
# #     from app.services.corpus_ingestion import CorpusIngestionService # Moved here
# #     db = next(deps.get_db())
# #     ingestion_service = CorpusIngestionService(db)
# #     ingestion_service.ingest_from_livelaw()


# # @celery_app.task
# # def embed_and_index_task(doc_id: int, content: str, metadata: dict):
# #     """Celery task to embed and index a document."""
# #     from app.services.document_indexer import DocumentIndexer
# #     indexer = DocumentIndexer()
# #     indexer.index_document(str(doc_id), content, metadata)

