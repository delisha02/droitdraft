
import re
from typing import List

def check_consistency(document: str) -> List[str]:
    """Checks the generated document for consistency.

    This function checks for any remaining placeholders in the format [placeholder].

    Args:
        document: The generated document.

    Returns:
        A list of found inconsistencies.
    """
    
    unfilled_placeholders = re.findall(r"\[(.*?)\]", document)
    
    errors = []
    if unfilled_placeholders:
        for placeholder in unfilled_placeholders:
            errors.append(f"Unfilled placeholder: [{placeholder}]")
            
    return errors
