
from typing import List, Dict, Any

def parse_search_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parses the search response and returns a list of documents."""
    return response.get("docs", [])

def parse_doc_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Parses the document response."""
    return response
