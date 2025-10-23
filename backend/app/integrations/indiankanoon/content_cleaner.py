
import re
from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """Removes HTML tags and artifacts from the given HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
        
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace in the given text."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_content(content: str) -> str:
    """Cleans the given content by removing HTML and normalizing whitespace."""
    cleaned_text = clean_html(content)
    normalized_text = normalize_whitespace(cleaned_text)
    return normalized_text
