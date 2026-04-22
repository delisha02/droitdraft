import asyncio
import httpx
from app.core.config import settings

async def get_parent():
    async with httpx.AsyncClient(
        base_url="https://api.indiankanoon.org",
        headers={"Authorization": f"Token {settings.INDIAN_KANOON_API_KEY}"}
    ) as client:
        # Get docmeta for section 138 of NI Act
        response = await client.post("/docmeta/1823824/")
        meta = response.json()
        print("Section 138 docmeta:")
        print(f"  Title: {meta.get('title')}")
        print(f"  ParentTid: {meta.get('parentTid')}")
        
        # Try to get the parent doc
        parent_tid = meta.get('parentTid')
        if parent_tid:
            response = await client.post(f"/docmeta/{parent_tid}/")
            parent_meta = response.json()
            print(f"\nParent document:")
            print(f"  Title: {parent_meta.get('title')}")
            print(f"  Tid: {parent_meta.get('tid')}")

if __name__ == "__main__":
    asyncio.run(get_parent())
