import asyncio
import os
import sys
from dotenv import load_dotenv

# Path to backend
BACKEND_DIR = os.path.join(os.getcwd(), "backend")
sys.path.append(BACKEND_DIR)

# Load .env from backend directory
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from app.db.database import SessionLocal
from app.models import models
from app.agents.legal_research.document_store import DocumentStore
from app.agents.legal_research.agent import LegalResearchAgent

async def verify():
    print("--- DroitDraft Verification Script ---")

    # 1. Check PostgreSQL
    print("\n[1] Checking PostgreSQL Database...")
    db = SessionLocal()
    try:
        template_count = db.query(models.Template).count()
        document_count = db.query(models.Document).count()
        user_count = db.query(models.User).count()
        print(f"✅ Templates found: {template_count}")
        print(f"✅ Documents found: {document_count}")
        print(f"✅ Users found: {user_count}")
    except Exception as e:
        print(f"❌ PostgreSQL Check Failed: {e}")
    finally:
        db.close()

    # 2. Check ChromaDB
    print("\n[2] Checking ChromaDB (Vector Store)...")
    try:
        store = DocumentStore()
        count = store.vector_store._collection.count()
        print(f"✅ Total Indexed Docs: {count}")
    except Exception as e:
        print(f"❌ ChromaDB Check Failed: {e}")

    # 3. Test Legal Research Agent
    print("\n[3] Testing Legal Research Agent...")
    try:
        agent = LegalResearchAgent()
        query = "What is the limitation period for a summary suit in India?"
        print(f"Query: '{query}'")
        print("Waiting for response from LLM...")
        result = await agent.answer_query(query)
        
        print("\n--- Agent Answer ---")
        print(result.get("answer"))
        print("\n--- Sources ---")
        for source in result.get("sources", []):
            print(f"- {source.get('title')} ({source.get('source')})")
        
        if "answer" in result and len(result["sources"]) > 0:
            print("\n✅ Legal Research Agent is working correctly!")
        else:
            print("\n⚠️ Legal Research Agent returned an empty or limited response.")
            
    except Exception as e:
        print(f"❌ Legal Research Test Failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
