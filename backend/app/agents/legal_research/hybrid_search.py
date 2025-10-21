
from typing import List, Dict, Any
from .query_analyzer import QueryAnalyzer
from .score_fusion import ScoreFusion
from .result_ranker import ResultRanker
from .bm25_engine import BM25Engine
from .dpr_engine import DPREngine
from ..document_processor.text_extractor import TextExtractor

class HybridSearch:
    """
    Orchestrates a hybrid search using BM25 and DPR.
    """

    def __init__(self, bm25_engine: BM25Engine, dpr_engine: DPREngine, document_retriever: TextExtractor, config: Dict[str, Any] = None):
        self.query_analyzer = QueryAnalyzer()
        self.score_fusion = ScoreFusion()
        self.result_ranker = ResultRanker()
        self.bm25_engine = bm25_engine
        self.dpr_engine = dpr_engine
        self.document_retriever = document_retriever
        self.config = config or self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "fusion_algorithm": "reciprocal_rank_fusion",
            "keyword_alpha": 0.7, # Weight for BM25 in keyword-heavy queries
            "semantic_alpha": 0.3, # Weight for BM25 in semantic queries
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

        if analysis["is_citation"]:
            # Simplified citation handling: route to BM25
            return self.bm25_engine.search(query, top_n=top_n)

        bm25_results = self.bm25_engine.search(query, top_n=top_n * 2) # Fetch more to have candidates for fusion
        dpr_results = self.dpr_engine.search(query, top_n=top_n * 2)

        alpha = self.config["keyword_alpha"] if analysis["type"] == "keyword" else self.config["semantic_alpha"]

        if self.config["fusion_algorithm"] == "reciprocal_rank_fusion":
            fused_results = self.score_fusion.reciprocal_rank_fusion([bm25_results, dpr_results], k=self.config["k"])
        elif self.config["fusion_algorithm"] == "weighted_linear_combination":
            fused_results = self.score_fusion.weighted_linear_combination(bm25_results, dpr_results, alpha=alpha)
        else:
            fused_results = self.score_fusion.reciprocal_rank_fusion([bm25_results, dpr_results], k=self.config["k"])

        # At this point, fused_results only contains IDs and scores.
        # We need to retrieve the full document content before re-ranking.
        doc_ids = [res["document"]["id"] for res in fused_results]
        # This is a placeholder for a document store retrieval method
        # In a real application, you would fetch this from a database or a document store
        retrieved_docs = {doc_id: self.document_retriever.get_document(doc_id) for doc_id in doc_ids}

        full_results = []
        for res in fused_results:
            doc_id = res["document"]["id"]
            if doc_id in retrieved_docs:
                full_results.append({"document": retrieved_docs[doc_id], "score": res["score"]})

        deduplicated_results = self.result_ranker.deduplicate(full_results)
        reranked_results = self.result_ranker.re_rank(deduplicated_results, boost_factors=self.config["boost_factors"])

        return reranked_results[:top_n]
