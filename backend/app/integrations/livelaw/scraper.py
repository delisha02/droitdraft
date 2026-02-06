
import httpx
import random
import asyncio
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup

from app.integrations.livelaw.parser import parse_article

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
]

class LiveLawScraper:
    BASE_URL = "https://www.livelaw.in"

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"User-Agent": random.choice(USER_AGENTS)},
            timeout=30.0
        )

    async def _get_random_delay(self) -> None:
        await asyncio.sleep(random.uniform(1, 5))

    async def _get_article_urls(self, url: str) -> List[str]:
        await self._get_random_delay()
        response = await self.client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extremely robust: look for any links with substantial text that aren't navigation
        article_links = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a['href']
            if len(text) > 40 and ("-" in href or "/top-stories/" in href):
                if href not in [l.get('href') for l in article_links]:
                    article_links.append(a)
        
        urls = [a["href"] for a in article_links if a.has_attr("href")]
        return list(set(urls)) # Return unique URLs

    async def scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        await self._get_random_delay()
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return parse_article(response.text)
        except httpx.HTTPStatusError as e:
            print(f"Error scraping {url}: {e}")
            return None

    async def scrape_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        latest_news_url = f"{self.BASE_URL}/top-stories"
        article_urls = await self._get_article_urls(latest_news_url)
        
        articles = []
        for url in article_urls[:limit]:
            # Ensure the URL is absolute
            if not url.startswith("http"):
                url = f"{self.BASE_URL}{url}"
            
            article = await self.scrape_article(url)
            if article:
                articles.append(article)
        
        return articles

    async def close(self):
        await self.client.aclose()
