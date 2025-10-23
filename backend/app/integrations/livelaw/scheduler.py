from app.celery_app import celery_app
from app.integrations.livelaw.scraper import LiveLawScraper
from app.integrations.livelaw.content_processor import LiveLawContentProcessor
from app.integrations.livelaw.storage import store_article
from app.api import deps

@celery_app.task
def scrape_livelaw_task():
    """Celery task to scrape, process, and store LiveLaw articles."""
    db = next(deps.get_db())
    scraper = LiveLawScraper()
    articles = scraper.scrape_latest_news()
    
    processed_articles = []
    for article in articles:
        processor = LiveLawContentProcessor(article)
        processed_article = processor.process()
        
        # Simple quality filter
        if processed_article["relevance_score"] > 0:
            store_article(db, processed_article)
            processed_articles.append(processed_article)

    print(f"Scraped and processed {len(processed_articles)} articles from LiveLaw.")
    scraper.close()