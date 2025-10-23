
import re
from typing import Dict, Any, Optional
from datetime import datetime

def extract_metadata(doc_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts and normalizes metadata from the document data."""
    metadata = {}

    # Extract and normalize date
    date_str = doc_data.get("date")
    if date_str:
        try:
            # Assuming date is in a format like "1950-05-26"
            metadata["date"] = datetime.fromisoformat(date_str).date()
        except ValueError:
            metadata["date"] = None
    
    # Normalize court name
    court_name = doc_data.get("court")
    if court_name:
        metadata["court"] = court_name.strip()
        
    # Extract other metadata
    metadata["title"] = doc_data.get("title", "").strip()
    metadata["doc_id"] = doc_data.get("doc_id")

    return metadata
