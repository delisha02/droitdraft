from .citation_parser import ParsedCitation

class CitationFormatter:
    """
    Formats a parsed legal citation.
    """

    def format(self, parsed_citation: ParsedCitation, style: str = "default") -> str:
        """
        Formats a parsed citation into a string.

        Args:
            parsed_citation: The parsed citation to format.
            style: The citation style to use (e.g., "default", "long", "short").

        Returns:
            A formatted citation string.
        """
        if not parsed_citation.journal:
            return parsed_citation.original_citation

        if style == "default":
            if parsed_citation.journal == "AIR":
                return f"{parsed_citation.year} AIR {parsed_citation.page_number}"
            elif parsed_citation.journal == "SCC":
                return f"({parsed_citation.year}) {parsed_citation.volume} SCC {parsed_citation.page_number}"
        
        return parsed_citation.original_citation
