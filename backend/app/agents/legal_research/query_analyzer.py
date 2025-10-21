
import re
from typing import Dict, Any, List
import spacy

class QueryAnalyzer:
    """
    Analyzes a search query to determine its characteristics.
    """

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spacy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analyzes the query and returns a dictionary of its characteristics.
        """
        doc = self.nlp(query)
        keywords = self._extract_keywords(doc)
        query_type = self._determine_query_type(doc, keywords)
        is_citation = self._is_legal_citation(query)

        return {
            "query": query,
            "type": query_type,
            "is_citation": is_citation,
            "keywords": keywords,
            "language": doc.lang_,
        }

    def _extract_keywords(self, doc) -> List[str]:
        """
        Extracts keywords from the query.
        """
        # Extract nouns, proper nouns, and entities
        keywords = set()
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                keywords.add(token.lemma_)
        for ent in doc.ents:
            keywords.add(ent.text)
        return list(keywords)

    def _determine_query_type(self, doc, keywords: List[str]) -> str:
        """
        Determines the type of the query (keyword-heavy vs. semantic).
        """
        # Simple heuristic: if the query is short and has many keywords, it's likely keyword-heavy
        if len(doc) <= 5 and len(keywords) >= 2:
            return "keyword"
        # If the query is a question, it's semantic
        if doc[0].pos_ == "AUX" or doc[0].tag_ == "WP":
            return "semantic"
        return "semantic" # Default to semantic

    def _is_legal_citation(self, query: str) -> bool:
        """
        Checks if the query is a legal citation.
        """
        citation_pattern = r'\b\d+\s[A-Z][\w\.]*\s\d+\b'
        return re.search(citation_pattern, query) is not None
