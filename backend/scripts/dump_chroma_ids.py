import os
import json
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def dump_ids():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    persist_directory = r"d:\droitdraft\backend\chroma_db"
    collection_name = "legal_judgments"
    
    if not os.path.exists(persist_directory):
        print(f"Directory {persist_directory} not found")
        return

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    
    # Get all documents
    all_docs = vectorstore.get()
    metadatas = all_docs.get("metadatas", [])
    
    ids = []
    for meta in metadatas:
        act = meta.get("act_name", "Unknown")
        sec = str(meta.get("section", "Unknown"))
        ids.append(f"{act}_{sec}")
    
    # Print unique IDs or first 20
    unique_ids = sorted(list(set(ids)))
    print(f"Total Unique IDs: {len(unique_ids)}")
    print("First 50 IDs:")
    for uid in unique_ids[:50]:
        print(uid)

if __name__ == "__main__":
    dump_ids()
