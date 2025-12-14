
from typing import TypedDict, List, Optional

class DroitAgentState(TypedDict):
    """Represents the state of the DroitDraft agent workflow."""
    
    # Input data
    query: str
    case_facts: dict
    template_id: Optional[int]
    
    # Processed data
    template_content: str
    document_title: str
    
    # Generated document
    generated_document: str
    
    # Research data
    research_query: Optional[str]
    research_results: Optional[List[dict]]
    
    # Error handling
    error: Optional[str]
