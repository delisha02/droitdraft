import asyncio
import os
import sys
from dotenv import load_dotenv

# Path setup
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)

# Load environment variables
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from app.agents.legal_research.agent import LegalResearchAgent

async def test_validation():
    agent = LegalResearchAgent()
    query = "What are the grounds for eviction under Maharashtra Rent Control Act Section 16?"
    print(f"Testing Query: {query}")
    
    # Use answer_query method as per agent.py
    results = await agent.answer_query(query)
    
    print("\n--- Research Results ---")
    answer = results.get('answer', '')
    print(f"Answer Sample:\n{answer[:500]}...")
    
    sources = results.get('sources', [])
    print(f"\nSources count: {len(sources)}")
    
    for i, src in enumerate(sources[:3]):
        print(f"\nSource {i+1}:")
        print(f"Title: {src.get('title')}")
        print(f"URL: {src.get('url')}")

if __name__ == "__main__":
    asyncio.run(test_validation())
