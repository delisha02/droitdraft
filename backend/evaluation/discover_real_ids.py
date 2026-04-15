import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure backend root is in path
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .env
load_dotenv(BACKEND_DIR / ".env")

from app.agents.legal_research.retrievers import get_persistent_retriever

def main():
    queries = [
        "Maharashtra Rent Control Act",
        "Bhartiya Nyaya Sanhita",
        "Code of Civil Procedure",
        "Negotiable Instruments Act Section 138"
    ]
    retriever = get_persistent_retriever()
    
    print("--- REAL CHROMADB ID DISCOVERY ---")
    for q in queries:
        print(f"\nQuery: {q}")
        try:
            docs = retriever.invoke(q)
            for i, doc in enumerate(docs[:3]):
                # Inspect common metadata fields for IDs
                doc_id = doc.metadata.get("id") or doc.metadata.get("source") or doc.metadata.get("doc_id")
                print(f"  Result {i+1}: ID={doc_id} | Title={doc.metadata.get('title', 'N/A')}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()
