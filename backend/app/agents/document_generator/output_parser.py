
import re

def parse_generated_document(llm_output: str) -> str:
    """Parses the LLM output to extract the generated document."""
    
    # The generated document is expected to be after the "**Generated Document:**" marker.
    # A simple approach is to split the string and take the last part.
    parts = llm_output.split("**Generated Document:**")
    if len(parts) > 1:
        return parts[-1].strip()
    
    # Fallback if the marker is not found
    return llm_output.strip()
