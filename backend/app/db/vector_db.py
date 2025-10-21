import chromadb
from app.core.config import settings

client = None

def get_vector_db():
    global client
    if client is None:
        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    return client
