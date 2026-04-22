import asyncio
from app.services.retrieval_service import RetrievalService

async def test_retrieval():
    service = RetrievalService()
    query = "Punishment for murder under Bhartiya Nyaya Sanhita"
    docs = service.retrieve_documents(query, strategy="hybrid", k=5)
    print(f"Query: {query}")
    for i, doc in enumerate(docs):
        meta = doc.metadata
        print(f"{i+1}. {meta.get('act_name')} Section {meta.get('section')}")

if __name__ == "__main__":
    asyncio.run(test_retrieval())
