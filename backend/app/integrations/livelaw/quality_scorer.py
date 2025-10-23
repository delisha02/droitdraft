
from typing import Dict, Any

LEGAL_KEYWORDS = [
    "Supreme Court", "High Court", "judgment", "petition", "advocate",
    "judge", "IPC", "CrPC", "Constitution", "section", "article"
]

def score_article(article: Dict[str, Any]) -> float:
    """Scores the relevance of an article based on legal keywords."""
    score = 0.0
    content = article.get("content", "").lower()
    title = article.get("title", "").lower()

    for keyword in LEGAL_KEYWORDS:
        if keyword.lower() in content or keyword.lower() in title:
            score += 1.0
            
    return score
