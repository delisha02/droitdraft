
from typing import List, Dict, Any
from datetime import datetime, timedelta

class ResultRanker:
    """
    Re-ranks fused search results.
    """

    def re_rank(self, results: List[Dict[str, Any]], boost_factors: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Re-ranks the results based on boost factors such as jurisdiction and recency.
        """
        if not boost_factors:
            return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        for result in results:
            score = result.get("score", 0)
            doc_metadata = result.get("document", {}).get("metadata", {})

            # Jurisdiction boost
            if "jurisdiction" in boost_factors and doc_metadata.get("jurisdiction") == boost_factors["jurisdiction"]:
                score *= boost_factors.get("jurisdiction_boost", 1.5)

            # Recency boost
            if "recency_days" in boost_factors and "date" in doc_metadata:
                try:
                    doc_date = datetime.fromisoformat(doc_metadata["date"])
                    if datetime.now() - doc_date < timedelta(days=boost_factors["recency_days"]):
                        score *= boost_factors.get("recency_boost", 1.2)
                except (ValueError, TypeError):
                    pass # Ignore if date is not in the correct format
            
            result["score"] = score

        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    def deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates results based on document ID, keeping the one with the highest score.
        """
        deduplicated_map = {}
        for result in results:
            doc_id = result.get("document", {}).get("id")
            if doc_id:
                if doc_id not in deduplicated_map or result.get("score", 0) > deduplicated_map[doc_id].get("score", 0):
                    deduplicated_map[doc_id] = result
        
        return list(deduplicated_map.values())
