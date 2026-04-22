import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def check_bns():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    persist_directory = r"d:\droitdraft\backend\chroma_db"
    collection_name = "legal_judgments"
    
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    
    # Use get() with metadata filter if possible, or just dump a few
    all_docs = vectorstore.get()
    metadatas = all_docs.get("metadatas", [])
    
    bns_count = 0
    unique_acts = set()
    for meta in metadatas:
        act = meta.get("act_name", "Unknown")
        unique_acts.add(act)
        if "Bhartiya Nyaya" in act:
            bns_count += 1
            
    print(f"Total docs in DB: {len(metadatas)}")
    print(f"BNS docs count: {bns_count}")
    print(f"Unique Acts: {sorted(list(unique_acts))}")

if __name__ == "__main__":
    check_bns()
