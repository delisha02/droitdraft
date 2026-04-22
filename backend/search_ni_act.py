import asyncio
from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder

async def search_ni_act():
    client = IndianKanoonClient()
    
    # Search for the main NI Act document
    builder = IndianKanoonQueryBuilder('"Negotiable Instruments Act, 1881" bare act')
    results = await client.search(builder)
    
    print("NI Act search results:")
    for r in results[:20]:
        print(f"  Title: {r.get('title')}")
        print(f"  Tid: {r.get('tid')}")
        print(f"  Type: {r.get('doctype')}")
        print()
    
    return results

if __name__ == "__main__":
    results = asyncio.run(search_ni_act())
