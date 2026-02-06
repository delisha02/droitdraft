
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from datetime import datetime

def parse_article(html_content: str) -> Optional[Dict[str, Any]]:
    """Parses the HTML of a LiveLaw article and extracts relevant information."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Updated to be extremely permissive
    title_tag = soup.select_one("h1.article-title, h1.article-title-six, h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Try several common article body identifiers
    content_tag = soup.select_one("div.article-body-container, div.article-body, div[class*='article-description'], .article-content, .story-full-width")
    
    if not content_tag:
        # Fallback: look for ANY div with a class containing 'body' or 'description' or 'content'
        for div in soup.find_all("div", class_=True):
            cls_str = " ".join(div.get("class", []))
            if any(k in cls_str.lower() for k in ['article-body', 'description', 'content', 'story-content']):
                if len(div.get_text(strip=True)) > 500:
                    content_tag = div
                    break
    
    content = content_tag.get_text(strip=True) if content_tag else None
    
    if not content:
        # Last resort: just find the biggest div
        divs = soup.find_all("div")
        if divs:
            biggest = max(divs, key=lambda d: len(d.get_text(strip=True)))
            if len(biggest.get_text(strip=True)) > 1000:
                content_tag = biggest
                content = content_tag.get_text(strip=True)

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
