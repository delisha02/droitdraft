import chromadb

def check_docker():
    try:
        client = chromadb.HttpClient(host="localhost", port=8000)
        collections = client.list_collections()
        print(f"Collections: {[c.name for c in collections]}")
        
        for coll_name in [c.name for c in collections]:
            coll = client.get_collection(coll_name)
            count = coll.count()
            print(f"Collection: {coll_name} | Count: {count}")
            
            # Get some metadata
            if count > 0:
                res = coll.get(limit=50)
                metas = res.get("metadatas", [])
                acts = set(m.get("act_name", "Unknown") for m in metas)
                print(f"  Acts found in sample: {acts}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_docker()
