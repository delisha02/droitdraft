import os
import sys
from dotenv import load_dotenv

# Path setup
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)

# Load environment variables
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from app.agents.legal_research.document_store import DocumentStore

def check_store():
    store = DocumentStore(persist_directory="chroma_db")
    # LangChain Chroma object exposes the underlying collection
    count = store.vector_store._collection.count()
    print(f"Total documents in ChromaDB collection '{store.collection_name}': {count}")
    
    # Peek at metadata of recent additions
    # Note: peek() returns 10 by default
    results = store.vector_store._collection.peek()
    if results and results['metadatas']:
        print("Sample Metadata:")
        for meta in results['metadatas'][:10]:
            print(f" - {meta.get('act_name')} / Section {meta.get('section')}")

if __name__ == "__main__":
    check_store()
