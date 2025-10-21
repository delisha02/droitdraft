
from typing import List, Dict, Any

class ScoreFusion:
    """
    Fuses scores from different search systems.
    """

    def _normalize_scores(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalizes scores using min-max normalization.
        """
        if not results:
            return []
        scores = [res.get("score", 0) for res in results]
        min_score, max_score = min(scores), max(scores)
        if max_score == min_score:
            return [{**res, "score": 1.0} for res in results]
        
        for res in results:
            res["score"] = (res.get("score", 0) - min_score) / (max_score - min_score)
        return results

    def reciprocal_rank_fusion(self, results_list: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
        """
        Performs Reciprocal Rank Fusion (RRF) on a list of search results.
        """
        fused_scores = {}
        for results in results_list:
            for i, result in enumerate(results):
                doc_id = result["document"]["id"]
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = 0
                fused_scores[doc_id] += 1 / (k + i + 1)

        reranked_results = sorted(fused_scores.items(), key=lambda item: item[1], reverse=True)
        return [{"document": {"id": doc_id}, "score": score} for doc_id, score in reranked_results]

    def weighted_linear_combination(self, bm25_results: List[Dict[str, Any]], dpr_results: List[Dict[str, Any]], alpha: float = 0.5) -> List[Dict[str, Any]]:
        """
        Combines scores using a weighted linear combination.
        """
        bm25_normalized = self._normalize_scores(bm25_results)
        dpr_normalized = self._normalize_scores(dpr_results)

        combined_scores = {}
        for res in bm25_normalized:
            combined_scores[res["document"]["id"]] = res["score"] * alpha
        
        for res in dpr_normalized:
            doc_id = res["document"]["id"]
            if doc_id not in combined_scores:
                combined_scores[doc_id] = 0
            combined_scores[doc_id] += res["score"] * (1 - alpha)

        reranked_results = sorted(combined_scores.items(), key=lambda item: item[1], reverse=True)
        return [{"document": {"id": doc_id}, "score": score} for doc_id, score in reranked_results]
