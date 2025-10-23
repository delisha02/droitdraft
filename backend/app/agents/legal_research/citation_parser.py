import re
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ParsedCitation:
    """
    Represents a parsed legal citation.
    """
    original_citation: str
    case_name: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[int] = None
    page_number: Optional[int] = None
    confidence_score: float = 0.0

class CitationParser:
    """
    Parses Indian legal citations from text.
    """

    CITATION_PATTERNS = {
        "AIR": re.compile(r"(\d{4})\s+AIR\s+(\d+)"),
        "SCC": re.compile(r"\((\d{4})\)\s+(\d+)\s+SCC\s+(\d+)"),
    }

    def parse(self, citation_text: str) -> Optional[ParsedCitation]:
        """
        Parses a single citation string.

        Args:
            citation_text: The citation string to parse.

        Returns:
            A ParsedCitation object if parsing is successful, otherwise None.
        """
        for journal, pattern in self.CITATION_PATTERNS.items():
            match = pattern.search(citation_text)
            if match:
                if journal == "AIR":
                    year, page = match.groups()
                    return ParsedCitation(
                        original_citation=citation_text,
                        year=int(year),
                        journal=journal,
                        volume=None,
                        page_number=int(page),
                        confidence_score=0.8
                    )
                elif journal == "SCC":
                    year, volume, page = match.groups()
                    return ParsedCitation(
                        original_citation=citation_text,
                        year=int(year),
                        journal=journal,
                        volume=int(volume),
                        page_number=int(page),
                        confidence_score=0.8
                    )
        return None

    def extract_citations(self, text: str) -> List[ParsedCitation]:
        """
        Extracts all citations from a block of text.

        Args:
            text: The text to extract citations from.

        Returns:
            A list of ParsedCitation objects.
        """
        # A more robust regex to find potential citations
        potential_citations = re.findall(r"\(?\d{4}\)?\s+\d*\s*\w+\s+\d+", text)
        
        parsed_citations = []
        for potential_citation in potential_citations:
            parsed = self.parse(potential_citation.strip())
            if parsed:
                parsed_citations.append(parsed)
        return parsed_citations
