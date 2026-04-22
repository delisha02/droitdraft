import os
from app.agents.legal_research.document_store import DocumentStore

store = DocumentStore()
count = store.vector_store._collection.count()
print(f"Total documents in ChromaDB: {count}")

# Check sample metadata
results = store.vector_store._collection.peek(5)
print("\nSample documents:")
for i, meta in enumerate(results['metadatas'][:5]):
    act = meta.get('act_name', 'Unknown')
    sec = meta.get('section', 'Unknown')
    print(f"  {i+1}. {act} / Section {sec}")
