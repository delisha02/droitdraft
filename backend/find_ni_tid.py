import asyncio
from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder

async def search_for_ni_act():
    client = IndianKanoonClient()
    
    # Search with different terms to find bare act
    search_terms = [
        "Negotiable Instruments Act 1881",
        "Negotiable Instruments 1881 bare act",
        "NI Act 1881",
    ]
    
    for term in search_terms:
        builder = IndianKanoonQueryBuilder(term)
        results = await client.search(builder)
        print(f"\nSearch: '{term}'")
        for r in results[:10]:
            doctype = r.get('doctype')
            title = r.get('title', '').replace('<b>', '').replace('</b>', '')
            print(f"  [{doctype}] {title} - tid:{r.get('tid')}")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(search_for_ni_act())
