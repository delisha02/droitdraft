import asyncio
import logging
from typing import List, Dict, Any

from app.agents.legal_research.document_store import DocumentStore
from app.integrations.livelaw.scraper import LiveLawScraper
from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchPipeline:
    """
    Orchestrates the ingestion of legal documents from various sources into the Vector Store.
    """
    
    def __init__(self, persist_directory: str = "chroma_db"):
        self.store = DocumentStore(persist_directory=persist_directory)
        
    async def ingest_livelaw_latest(self, limit: int = 10):
        """
        Scrapes and ingests the latest news/judgments from LiveLaw.
        """
        scraper = LiveLawScraper()
        try:
            logger.info("Starting LiveLaw scrape...")
            # Note: scrape_latest_news in scraper.py currently doesn't accept a limit, 
            # but we can slice the result if needed or modify scraper later.
            articles = await scraper.scrape_latest_news()
            
            if not articles:
                logger.warning("No articles found on LiveLaw.")
                return

            logger.info(f"Found {len(articles)} articles. Processing...")
            
            # Filter and Prepare
            docs_to_ingest = []
            for article in articles[:limit]:
                if not article.get('content'):
                    continue
                
                # Enrich metadata if needed
                article['source'] = 'LiveLaw'
                article['type'] = 'news_judgment'
                docs_to_ingest.append(article)
            
            if docs_to_ingest:
                logger.info(f"Ingesting {len(docs_to_ingest)} valid documents into ChromaDB...")
                # offload to synchronous store method (Chroma operations are sync in this version usually)
                # If store operations are heavy, might need run_in_executor
                self.store.add_documents(docs_to_ingest, content_key='content')
                logger.info("Ingestion complete.")
            else:
                logger.info("No valid content to ingest.")
                
        except Exception as e:
            logger.error(f"Error during LiveLaw ingestion: {e}", exc_info=True)
        finally:
            await scraper.close()

    async def ingest_indian_kanoon(self, query: str = "Maharashtra High Court", limit: int = 10):
        """
        Searches and ingests documents from Indian Kanoon.
        """
        client = IndianKanoonClient()
        try:
            logger.info(f"Starting Indian Kanoon search for query: {query}...")
            query_builder = IndianKanoonQueryBuilder(query)
            # You can add filters if needed
            # query_builder.with_doctypes(["judgments"])
            
            search_results = await client.search(query_builder)
            
            if not search_results:
                logger.warning("No search results found on Indian Kanoon.")
                return

            logger.info(f"Found {len(search_results)} search results. Fetching details...")
            
            docs_to_ingest = []
            for res in search_results[:limit]:
                doc_id = res.get('tid')
                if not doc_id:
                    continue
                
                logger.info(f"Fetching document detail for tid: {doc_id}...")
                doc_detail = await client.doc(str(doc_id))
                
                content = doc_detail.get('doc') or doc_detail.get('content')
                if not content:
                    continue
                
                doc_to_save = {
                    "title": doc_detail.get('title') or res.get('title'),
                    "content": content,
                    "source": "IndianKanoon",
                    "doc_id": str(doc_id),
                    "url": f"https://indiankanoon.org/doc/{doc_id}/"
                }
                docs_to_ingest.append(doc_to_save)
            
            if docs_to_ingest:
                logger.info(f"Ingesting {len(docs_to_ingest)} documents from Indian Kanoon into ChromaDB...")
                self.store.add_documents(docs_to_ingest, content_key='content')
                logger.info("Indian Kanoon ingestion complete.")
            else:
                logger.info("No valid Indian Kanoon content to ingest.")
                
        except Exception as e:
            logger.error(f"Error during Indian Kanoon ingestion: {e}", exc_info=True)
        finally:
            await client.close()

    async def search_legal_memory(self, query: str, k: int = 5):
        """
        Searches the ingested legal memory.
        """
        results = self.store.search(query, k=k)
        return results

async def run_ingestion():
    pipeline = ResearchPipeline()
    # Ingest LiveLaw
    await pipeline.ingest_livelaw_latest(limit=5)
    # Ingest Indian Kanoon
    await pipeline.ingest_indian_kanoon(query="Maharashtra High Court", limit=5)
    await pipeline.ingest_indian_kanoon(query="Bombay High Court", limit=5)

if __name__ == "__main__":
    asyncio.run(run_ingestion())
