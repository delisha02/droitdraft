import chromadb
from app.core.config import settings

client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)

def get_vector_db():
    return client
