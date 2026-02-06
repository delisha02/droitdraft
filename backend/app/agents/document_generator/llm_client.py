
import time
import asyncio
from typing import Optional, Dict, Any, List

import backoff
import google.generativeai as genai
from groq import Groq

from app.core.config import settings

# --- Monkeypatch for httpx 0.28.1 compatibility with legacy SDKs ---
import httpx

# Patch Sync Client
original_httpx_init = httpx.Client.__init__
def patched_httpx_init(self, *args, **kwargs):
    if 'proxies' in kwargs:
        kwargs['proxy'] = kwargs.pop('proxies')
    original_httpx_init(self, *args, **kwargs)
httpx.Client.__init__ = patched_httpx_init

# Patch Async Client
original_async_httpx_init = httpx.AsyncClient.__init__
def patched_async_httpx_init(self, *args, **kwargs):
    if 'proxies' in kwargs:
        kwargs['proxy'] = kwargs.pop('proxies')
    original_async_httpx_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = patched_async_httpx_init
# ------------------------------------------------------------------

# Configuration
GROQ_API_KEY = settings.GROQ_API_KEY
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Configure Gemini
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except:
        pass

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

# Groq has a rate limit of 14400 requests per day for free tier, but 30 requests per minute usually.
groq_rate_limiter = SimpleRateLimiter(rate_limit=25, period=60)

class LLMClient:
    def __init__(self, groq_client: Optional[object] = None, gemini_model: Optional[genai.GenerativeModel] = None):
        if GROQ_API_KEY and GROQ_API_KEY.strip():
            self.groq_client = groq_client or Groq(api_key=GROQ_API_KEY)
            print("Groq client initialized.")
        else:
            self.groq_client = None

        if GEMINI_API_KEY and GEMINI_API_KEY.strip():
            print(f"Gemini configuring with key: {GEMINI_API_KEY[:4]}...{GEMINI_API_KEY[-4:]}")
            # Try to use a manually specified model if provided
            manual_model = getattr(settings, "GEMINI_MODEL", None)
            
            # List of models to try in order of preference (only valid models)
            pref_models = [
                'gemini-1.5-flash',
                'gemini-1.5-pro',
                'gemini-pro',
            ]
            
            self.candidate_models = []
            if manual_model:
                self.candidate_models.append(manual_model)
            
            for m in pref_models:
                self.candidate_models.append(m)
                self.candidate_models.append(f"models/{m}")

            self.gemini_model = None
            for model_name in self.candidate_models:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    print(f"Gemini initialized with candidate model: {model_name}")
                    break
                except Exception as e:
                    continue
            
            if not self.gemini_model:
                print("Warning: All Gemini candidate models failed to initialize.")
        else:
            self.gemini_model = None


    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    async def generate_with_groq(self, prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
        if not self.groq_client:
            raise ValueError("Groq client not configured. Please provide a GROQ_API_KEY.")
        
        await groq_rate_limiter.wait()

        # Run synchronous Groq call in a thread pool to avoid blocking FastAPI
        loop = asyncio.get_event_loop()
        chat_completion = await loop.run_in_executor(
            None,
            lambda: self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                temperature=0.7,
                max_tokens=4096,
            )
        )
        return chat_completion.choices[0].message.content

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def generate_with_gemini(self, prompt: str) -> str:
        if not self.gemini_model:
            raise ValueError("Gemini client not configured. Check your API key.")
        
        # Determine starting index for fallback
        current_model_name = self.gemini_model.model_name
        try:
            # Match either with or without prefix
            best_match = current_model_name.replace('models/', '')
            start_idx = self.candidate_models.index(best_match)
        except ValueError:
            start_idx = 0
            
        last_error = None
        for i in range(start_idx, len(self.candidate_models)):
            target_model_name = self.candidate_models[i]
            try:
                if self.gemini_model.model_name != target_model_name and self.gemini_model.model_name != f"models/{target_model_name}":
                    print(f"Trying fallback: {target_model_name}")
                    self.gemini_model = genai.GenerativeModel(target_model_name)
                
                genai.configure(api_key=settings.GEMINI_API_KEY)
                response = await self.gemini_model.generate_content_async(prompt)
                
                if not response:
                    continue

                try:
                    return response.text
                except ValueError:
                    if response.candidates:
                        try:
                            return response.candidates[0].content.parts[0].text
                        except: pass
                    continue 
                    
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                if "notfound" in error_msg or "404" in error_msg or "not found" in error_msg:
                    continue
                else:
                    raise e
        
        if last_error:
            raise last_error
        return "Error: All Gemini model candidates failed."

    async def generate(self, prompt: str, use_groq: bool = True) -> str:
        # Prioritize Groq if available
        if self.groq_client and use_groq:
            try:
                return await self.generate_with_groq(prompt)
            except Exception as e:
                print(f"Groq generation failed: {e}. Falling back to Gemini...")
        
        # Fallback to Gemini
        if self.gemini_model:
            return await self.generate_with_gemini(prompt)
        else:
            raise ValueError("No LLM client configured. Please provide a GROQ_API_KEY or GEMINI_API_KEY.")

llm_client = LLMClient()
