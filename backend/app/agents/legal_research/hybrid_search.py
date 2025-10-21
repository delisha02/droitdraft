
from typing import List, Dict, Any
from .query_analyzer import QueryAnalyzer
from .score_fusion import ScoreFusion
from .result_ranker import ResultRanker
from .document_store import DocumentStore

class HybridSearch:
    """
    Orchestrates a hybrid search using multiple search engines.
    """

    def __init__(self, search_engines: List[Any], document_store: DocumentStore, config: Dict[str, Any] = None):
        self.query_analyzer = QueryAnalyzer()
        self.score_fusion = ScoreFusion()
        self.result_ranker = ResultRanker()
        self.search_engines = search_engines
        self.document_store = document_store
        self.config = config or self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "fusion_algorithm": "reciprocal_rank_fusion",
            "k": 60, # For RRF
            "boost_factors": {
                "jurisdiction": "US",
                "jurisdiction_boost": 1.5,
                "recency_days": 365,
                "recency_boost": 1.2
            }
        }

    def search(self, query: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Performs a hybrid search.
        """
        analysis = self.query_analyzer.analyze(query)

        all_results = []
        for engine in self.search_engines:
            results = engine.search(query, top_n=top_n * 2)
            all_results.append(results)

        if self.config["fusion_algorithm"] == "reciprocal_rank_fusion":
            fused_results = self.score_fusion.reciprocal_rank_fusion(all_results, k=self.config["k"])
        else:
            # As a default, use the first engine's results if fusion algorithm is not specified
            fused_results = all_results[0] if all_results else []

        doc_ids = [res["document"]["id"] for res in fused_results]
        retrieved_docs = {doc_id: self.document_store.get_document(doc_id) for doc_id in doc_ids}

        full_results = []
        for res in fused_results:
            doc_id = res["document"]["id"]
            if doc_id in retrieved_docs:
                full_results.append({"document": retrieved_docs[doc_id], "score": res["score"]})

        deduplicated_results = self.result_ranker.deduplicate(full_results)
        reranked_results = self.result_ranker.re_rank(deduplicated_results, boost_factors=self.config["boost_factors"])

        return reranked_results[:top_n]
