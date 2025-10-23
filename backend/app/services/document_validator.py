
from typing import Dict, Any, List

REQUIRED_METADATA = ["title", "content"]

def validate_document(doc_data: Dict[str, Any]) -> List[str]:
    """Validates the document data for required metadata."""
    errors = []
    for field in REQUIRED_METADATA:
        if field not in doc_data or not doc_data[field]:
            errors.append(f"Missing required metadata field: {field}")
    return errors
