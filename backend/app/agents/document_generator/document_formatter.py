from typing import List

def format_document(title: str, sections: List[str]) -> str:
    """Formats the final document.

    Args:
        title: The title of the document.
        sections: A list of generated sections.

    Returns:
        The formatted document as a string.
    """
    
    document = f"# {title}\n\n"
    document += "\n\n".join(sections)
    
    return document
