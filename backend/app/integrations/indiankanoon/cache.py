
import aioredis
import json
from typing import Optional, Any

from app.core.config import settings

class RedisCache:
    def __init__(self, host: str = settings.REDIS_HOST, port: int = settings.REDIS_PORT, db: int = 0):
        self.redis = aioredis.from_url(f"redis://{host}:{port}/{db}")

    async def get(self, key: str) -> Optional[Any]:
        cached_data = await self.redis.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    async def set(self, key: str, value: Any, expire: int = 3600):
        await self.redis.set(key, json.dumps(value), ex=expire)

    async def close(self):
        await self.redis.close()
