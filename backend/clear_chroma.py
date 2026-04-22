import shutil
import os

# Clear existing ChromaDB
chroma_dir = "chroma_db"
if os.path.exists(chroma_dir):
    shutil.rmtree(chroma_dir)
    print(f"Deleted existing {chroma_dir}")
else:
    print(f"{chroma_dir} does not exist")

# Also delete any lock files
for f in os.listdir("."):
    if f.startswith(".chroma"):
        os.remove(f)
        print(f"Deleted {f}")
