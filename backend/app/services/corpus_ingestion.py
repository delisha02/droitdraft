
from sqlalchemy.orm import Session

from app.integrations.indiankanoon.data_processor import IndianKanoonDataProcessor
from app.integrations.livelaw.scraper import LiveLawScraper
from app.integrations.livelaw.content_processor import LiveLawContentProcessor
from app.integrations.livelaw.storage import store_article
from app.services.document_validator import validate_document
from app.services.ingestion_monitor import ingestion_monitor

class CorpusIngestionService:
    def __init__(self, db: Session):
        self.db = db

    async def ingest_from_indian_kanoon(self, doc_id: str):
        source = "indian_kanoon"
        try:
            processor = IndianKanoonDataProcessor(self.db)
            await processor.process_document(doc_id)
            ingestion_monitor.log_success(source)
        except Exception as e:
            ingestion_monitor.log_failure(source)
            print(f"Error ingesting from Indian Kanoon: {e}")

    async def ingest_from_livelaw(self):
        source = "livelaw"
        try:
            scraper = LiveLawScraper()
            articles = await scraper.scrape_latest_news()
            for article in articles:
                errors = validate_document(article)
                if errors:
                    print(f"Validation failed for article: {article.get('title')}. Errors: {errors}")
                    continue

                processor = LiveLawContentProcessor(article)
                processed_article = processor.process()
                store_article(self.db, processed_article)
            ingestion_monitor.log_success(source)
        except Exception as e:
            ingestion_monitor.log_failure(source)
            print(f"Error ingesting from LiveLaw: {e}")

    async def ingest_from_upload(self, file_content: str, metadata: dict):
        source = "upload"
        try:
            # For uploaded files, we can create a simple article structure
            article = {
                "title": metadata.get("title", "Uploaded Document"),
                "content": file_content,
                "publication_date": metadata.get("publication_date"),
            }
            errors = validate_document(article)
            if errors:
                raise ValueError(f"Validation failed: {errors}")

            processor = LiveLawContentProcessor(article) # Reusing the processor for now
            processed_article = processor.process()
            store_article(self.db, processed_article)
            ingestion_monitor.log_success(source)
        except Exception as e:
            ingestion_monitor.log_failure(source)
            print(f"Error ingesting from upload: {e}")
