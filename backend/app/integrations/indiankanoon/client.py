import os
import httpx
from typing import Optional, Dict, Any, List
from pybreaker import CircuitBreaker

from app.integrations.indiankanoon.exceptions import APIKeyNotFoundError, APIError
from app.integrations.indiankanoon.rate_limiter import RateLimiter
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder
from app.integrations.indiankanoon.response_parser import parse_search_response, parse_doc_response
from app.integrations.indiankanoon.cache import RedisCache

from app.core.config import settings

# Circuit Breaker configuration
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

class IndianKanoonClient:
    BASE_URL = "https://api.indiankanoon.org"

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[RedisCache] = None
    ):
        self.api_key = api_key or settings.INDIAN_KANOON_API_KEY
        if not self.api_key:
            raise APIKeyNotFoundError("Indian Kanoon API key not found.")
        
        self.rate_limiter = rate_limiter or RateLimiter()
        self.cache = cache or RedisCache()
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Token {self.api_key}",
                "Accept": "application/json",
                "User-Agent": "DroitDraft/1.0"
            }
        )

    @breaker
    async def _request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        cache_key = f"{method}:{url}:{kwargs}"
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            return cached_response

        await self.rate_limiter.wait()
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            json_response = response.json()
            await self.cache.set(cache_key, json_response)
            return json_response
        except httpx.HTTPStatusError as e:
            raise APIError(e.response.status_code, e.response.text)
        except httpx.RequestError as e:
            raise APIError(0, str(e))

    async def search(self, query_builder: IndianKanoonQueryBuilder, pagenum: int = 0) -> List[Dict[str, Any]]:
        query = query_builder.build()
        data = {"formInput": query, "pagenum": pagenum}
        response = await self._request("POST", "/search/", data=data)
        return parse_search_response(response)

    async def doc(self, doc_id: str) -> Dict[str, Any]:
        response = await self._request("POST", f"/doc/{doc_id}/")
        return parse_doc_response(response)

    async def docmeta(self, doc_id: str) -> Dict[str, Any]:
        return await self._request("GET", f"/docmeta/{doc_id}/")

    async def docfragment(self, doc_id: str, query: str) -> Dict[str, Any]:
        data = {"formInput": query}
        return await self._request("POST", f"/docfragment/{doc_id}/", data=data)

    async def close(self):
        await self.client.aclose()
        await self.cache.close()