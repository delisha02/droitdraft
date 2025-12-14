
# import os
import time
import asyncio
from typing import Optional, Dict, Any, List

import backoff
import google.generativeai as genai
# from groq import Groq, RateLimitError

from app.core.config import settings

# Configuration
# GROQ_API_KEY = settings.GROQ_API_KEY
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Rate limiting
class SimpleRateLimiter:
    def __init__(self, rate_limit: int, period: int):
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

# Groq has a rate limit of 60 requests per minute
# groq_rate_limiter = SimpleRateLimiter(rate_limit=55, period=60)

class LLMClient:
    def __init__(self, groq_client: Optional[object] = None, gemini_model: Optional[genai.GenerativeModel] = None):
        # if GROQ_API_KEY and GROQ_API_KEY.strip():
        #     self.groq_client = groq_client or Groq(api_key=GROQ_API_KEY)
        # else:
        self.groq_client = None

        if GEMINI_API_KEY and GEMINI_API_KEY.strip():
            self.gemini_model = gemini_model or genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None


    # @backoff.on_exception(backoff.expo, RateLimitError, max_tries=5)
    # async def generate_with_groq(self, prompt: str, model: str = "llama-3.1-8b-instant") -> str:
    #     if not self.groq_client:
    #         raise ValueError("Groq client not configured. Please provide a GROQ_API_KEY.")
        
    #     await groq_rate_limiter.wait()

    #     chat_completion = self.groq_client.chat.completions.create(
    #         messages=[{"role": "user", "content": prompt}],
    #         model=model,
    #         temperature=0.7,
    #         max_tokens=4096,
    #     )
    #     return chat_completion.choices[0].message.content

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    async def generate_with_gemini(self, prompt: str) -> str:
        if not self.gemini_model:
            raise ValueError("Gemini client not configured. Please provide a GEMINI_API_KEY.")
        
        response = await self.gemini_model.generate_content_async(prompt)
        return response.text

    async def generate(self, prompt: str, use_groq: bool = True) -> str:
        # if use_groq and self.groq_client:
        #     try:
        #         return await self.generate_with_groq(prompt)
        #     except Exception as e:
        #         print(f"Groq generation failed: {e}. Falling back to Gemini.")
        #         if self.gemini_model:
        #             return await self.generate_with_gemini(prompt)
        #         else:
        #             raise
        # elif self.gemini_model:
        if self.gemini_model:
            return await self.generate_with_gemini(prompt)
        else:
            raise ValueError("No LLM client configured. Please provide a GROQ_API_KEY or GEMINI_API_KEY.")

llm_client = LLMClient()
