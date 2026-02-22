import asyncio
import os
import sys
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Path setup
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)

# Load environment variables
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from app.agents.legal_research.document_store import DocumentStore
from app.integrations.indiankanoon.client import IndianKanoonClient

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BulkIngest")

class StatuteIngestor:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.store = DocumentStore(persist_directory=persist_directory)
        self.client = IndianKanoonClient()
        self.tracking_file = os.path.abspath(os.path.join(BACKEND_DIR, "..", "docs", "ingested_data.md"))

    def clean_html(self, html_text: str) -> str:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def extract_sec_num(self, html_part: str) -> str:
        # Try id="section_123"
        id_match = re.search(r'id="section_(\d+[A-Z]?)"', html_part)
        if id_match: return id_match.group(1)
        
        # Try <h3>...123. ...</h3>
        h3_match = re.search(r'<h3>.*?(\d+[A-Z]?)\..*?</h3>', html_part, re.DOTALL)
        if h3_match: return h3_match.group(1)
        
        # Try any anchor /doc/number/
        doc_match = re.search(r'/doc/\d+/">(\d+[A-Z]?)\.', html_part)
        if doc_match: return doc_match.group(1)
        
        return "Unknown"

    def chunk_by_sections(self, content: str, act_name: str) -> List[Dict[str, Any]]:
        sections = []
        
        # Primary: Akoma Ntoso splitting
        if 'class="akn-section"' in content:
            # We split by <section class="akn-section"
            parts = re.split(r'<section\s+class="akn-section"', content)
            preamble = self.clean_html(parts[0])
            if preamble:
                sections.append({"content": preamble, "metadata": {"act_name": act_name, "section": "Preamble", "doc_type": "statute", "jurisdiction": "India"}})
            
            for part in parts[1:]:
                full_part = '<section class="akn-section"' + part
                sec_num = self.extract_sec_num(full_part)
                clean_content = self.clean_html(full_part)
                if clean_content:
                    sections.append({"content": clean_content, "metadata": {"act_name": act_name, "section": sec_num, "doc_type": "statute", "jurisdiction": "India"}})
        
        # Secondary: h3 tag splitting if primary failed (fell back to 1 chunk)
        if len(sections) < 5 and '<h3>' in content:
             logger.info(f"Falling back to <h3> splitting for {act_name}")
             sections = []
             parts = re.split(r'<h3>', content)
             preamble = self.clean_html(parts[0])
             if preamble:
                 sections.append({"content": preamble, "metadata": {"act_name": act_name, "section": "Preamble", "doc_type": "statute", "jurisdiction": "India"}})
             for part in parts[1:]:
                 full_part = '<h3>' + part
                 sec_num = self.extract_sec_num(full_part)
                 clean_content = self.clean_html(full_part)
                 if clean_content:
                     sections.append({"content": clean_content, "metadata": {"act_name": act_name, "section": sec_num, "doc_type": "statute", "jurisdiction": "India"}})
        
        # Ternary: Plain text fallback
        if len(sections) < 5:
             logger.info(f"Falling back to Plain Text regex for {act_name}")
             sections = []
             section_pattern = r'\n(?:\s*Section\s+)?(\d+[A-Z]?)\.\s+'
             parts = re.split(section_pattern, "\n" + content)
             if parts[0].strip():
                 sections.append({"content": parts[0].strip(), "metadata": {"act_name": act_name, "section": "Preamble"}})
             for i in range(1, len(parts), 2):
                 sections.append({"content": f"Section {parts[i]}\n{parts[i+1].strip()}", "metadata": {"act_name": act_name, "section": parts[i]}})
        
        # Final safety: Add metadata common fields
        for sec in sections:
            sec["metadata"]["doc_type"] = "statute"
            sec["metadata"]["jurisdiction"] = "India"
            if "act_name" not in sec["metadata"]: sec["metadata"]["act_name"] = act_name
            
        return sections

    async def ingest_act(self, act_display_name: str, tid: int):
        logger.info(f"==> Ingesting: {act_display_name} (TID: {tid})")
        try:
            doc_data = await self.client.doc(str(tid))
            content = doc_data.get('doc') or doc_data.get('content')
            if not content: return
            chunks = self.chunk_by_sections(content, act_display_name)
            logger.info(f"Split into {len(chunks)} sections.")
            if chunks:
                self.store.add_documents(chunks, content_key="content")
                self.update_tracking(act_display_name, len(chunks))
        except Exception as e:
            logger.error(f"Failed {act_display_name}: {e}")

    def update_tracking(self, act_name: str, count: int):
        if not os.path.exists(self.tracking_file): return
        try:
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                content = f.read()
            date_str = datetime.now().strftime("%Y-%m-%d")
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if act_name in line:
                    if "Priority 1" in line: priority = "Priority 1"
                    elif "Priority 2" in line: priority = "Priority 2"
                    else: priority = "Priority 1"
                    new_lines.append(f"| {act_name} | ✅ Ingested | {count} sections | {date_str} | {priority} |")
                else:
                    new_lines.append(line)
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
        except Exception as e:
            logger.error(f"Tracking failed: {e}")

async def main():
    ingestor = StatuteIngestor()
    acts = [
        {"name": "Bhartiya Nyaya Sanhita (BNS)", "tid": 149679501},
        {"name": "Bhartiya Nagarik Suraksha Sanhita (BNSS)", "tid": 91117739},
        {"name": "Bhartiya Sakshya Adhiniyam (BSA)", "tid": 70224818},
        {"name": "Code of Civil Procedure (CPC)", "tid": 161831507},
        {"name": "Indian Contract Act, 1872", "tid": 171398},
        {"name": "Indian Succession Act, 1925", "tid": 1450343},
        {"name": "Registration Act, 1908", "tid": 1489134},
        {"name": "Specific Relief Act, 1963", "tid": 1671917},
        {"name": "Transfer of Property Act, 1882", "tid": 515323},
        {"name": "Maharashtra Rent Control Act", "tid": 196692406},
        {"name": "Maharashtra Co-operative Societies Act", "tid": 34627769},
    ]
    for act in acts:
        await ingestor.ingest_act(act["name"], act["tid"])
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
