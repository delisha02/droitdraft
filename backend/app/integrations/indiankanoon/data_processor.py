
from sqlalchemy.orm import Session

from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.content_cleaner import clean_content
from app.integrations.indiankanoon.metadata_extractor import extract_metadata
from app.integrations.indiankanoon.deduplicator import generate_fingerprint
from app.integrations.indiankanoon.storage import store_document

class IndianKanoonDataProcessor:
    def __init__(self, db: Session):
        self.client = IndianKanoonClient()
        self.db = db
        self.processed_fingerprints = set()

    async def process_document(self, doc_id: str):
        """Fetches, processes, and stores a single document from Indian Kanoon."""
        
        # 1. Fetch data
        doc_data = await self.client.doc(doc_id)
        
        # 2. Clean content
        # The actual content is in the 'doc' field of the response
        raw_content = doc_data.get("doc", "")
        cleaned_content = clean_content(raw_content)
        
        # 3. Deduplication
        fingerprint = generate_fingerprint(cleaned_content)
        if fingerprint in self.processed_fingerprints:
            print(f"Document {doc_id} is a duplicate, skipping.")
            return
        self.processed_fingerprints.add(fingerprint)
        
        # 4. Extract metadata
        metadata = extract_metadata(doc_data)
        
        # 5. Store data
        store_document(self.db, metadata, cleaned_content)
        print(f"Successfully processed and stored document {doc_id}")

    async def close(self):
        await self.client.close()
