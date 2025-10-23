
import re
from typing import Dict, Any, List

def enrich_metadata(article: Dict[str, Any]) -> Dict[str, Any]:
    """Enriches the article metadata by extracting case references."""
    content = article.get("content", "")
    
    # Simple regex to find patterns like "Case No. 123/2023"
    case_references = re.findall(r"Case No\.\s*\d+/\d+", content, re.IGNORECASE)
    
    article["case_references"] = list(set(case_references))
    return article
