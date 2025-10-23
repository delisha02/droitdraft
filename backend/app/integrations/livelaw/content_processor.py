
from typing import Dict, Any

from app.integrations.livelaw.quality_scorer import score_article
from app.integrations.livelaw.deduplicator import generate_fingerprint
from app.integrations.livelaw.metadata_enricher import enrich_metadata

class LiveLawContentProcessor:
    def __init__(self, article: Dict[str, Any]):
        self.article = article
        self.fingerprint = None
        self.score = 0.0

    def process(self) -> Dict[str, Any]:
        """Processes the article by scoring, fingerprinting, and enriching it."""
        
        # 1. Score article
        self.score = score_article(self.article)
        self.article["relevance_score"] = self.score
        
        # 2. Generate fingerprint for deduplication
        self.fingerprint = generate_fingerprint(self.article["content"])
        self.article["fingerprint"] = self.fingerprint
        
        # 3. Enrich metadata
        self.article = enrich_metadata(self.article)
        
        return self.article
