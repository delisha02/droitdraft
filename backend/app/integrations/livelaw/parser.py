
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime

def parse_article(html_content: str) -> Optional[Dict[str, Any]]:
    """Parses the HTML of a LiveLaw article and extracts relevant information."""
    soup = BeautifulSoup(html_content, "html.parser")

    title_tag = soup.find("h1", class_="article-title")
    title = title_tag.get_text(strip=True) if title_tag else None

    content_tag = soup.find("div", class_="article-body")
    content = content_tag.get_text(strip=True) if content_tag else None

    date_tag = soup.find("time")
    date_str = date_tag["datetime"] if date_tag and date_tag.has_attr("datetime") else None
    
    publication_date = None
    if date_str:
        try:
            publication_date = datetime.fromisoformat(date_str)
        except ValueError:
            pass

    if not title or not content:
        return None

    return {
        "title": title,
        "content": content,
        "publication_date": publication_date,
    }
