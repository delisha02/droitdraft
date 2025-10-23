
import time
import asyncio

class RateLimiter:
    def __init__(self, rate_limit: int = 5, period: int = 60):
        self.rate_limit = rate_limit
        self.period = period
        self.requests = []

    async def wait(self):
        while True:
            now = time.time()
            self.requests = [req for req in self.requests if now - req < self.period]
            if len(self.requests) < self.rate_limit:
                self.requests.append(now)
                break
            await asyncio.sleep(self.period - (now - self.requests[0]))
