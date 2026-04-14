import argparse
import asyncio
import logging
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from dotenv import load_dotenv

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from app.agents.legal_research.document_store import DocumentStore
from app.integrations.indiankanoon.client import IndianKanoonClient
from app.integrations.indiankanoon.query_builder import IndianKanoonQueryBuilder
from app.services.legal_corpus_catalog import (
    get_legal_research_act_catalog,
    match_catalog_entries,
    normalize_legal_title,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BulkIngest")


class LegalCorpusIngestor:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.store = DocumentStore(persist_directory=persist_directory)
        self.client = IndianKanoonClient()
        self.tracking_file = os.path.abspath(os.path.join(BACKEND_DIR, "..", "docs", "ingested_data.md"))

    def clean_html(self, html_text: str) -> str:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def extract_sec_num(self, html_part: str) -> str:
        id_match = re.search(r'id="section_(\d+[A-Z]?)"', html_part)
        if id_match:
            return id_match.group(1)

        h3_match = re.search(r"<h3>.*?(\d+[A-Z]?)\..*?</h3>", html_part, re.DOTALL)
        if h3_match:
            return h3_match.group(1)

        doc_match = re.search(r'/doc/\d+/">(\d+[A-Z]?)\.', html_part)
        if doc_match:
            return doc_match.group(1)

        return "Unknown"

    def build_chunk_text(self, act_name: str, section: str, clean_content: str) -> str:
        header = act_name
        if section:
            header += f"\nSection {section}"
        return f"{header}\n\n{clean_content}".strip()

    def chunk_by_sections(self, content: str, act_name: str, doc_type: str = "statute", jurisdiction: str = "India") -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []

        if 'class="akn-section"' in content:
            parts = re.split(r'<section\s+class="akn-section"', content)
            preamble = self.clean_html(parts[0])
            if preamble:
                sections.append(
                    {
                        "content": self.build_chunk_text(act_name, "Preamble", preamble),
                        "metadata": {
                            "act_name": act_name,
                            "section": "Preamble",
                            "doc_type": doc_type,
                            "jurisdiction": jurisdiction,
                        },
                    }
                )

            for part in parts[1:]:
                full_part = '<section class="akn-section"' + part
                sec_num = self.extract_sec_num(full_part)
                clean_content = self.clean_html(full_part)
                if clean_content:
                    sections.append(
                        {
                            "content": self.build_chunk_text(act_name, sec_num, clean_content),
                            "metadata": {
                                "act_name": act_name,
                                "section": sec_num,
                                "doc_type": doc_type,
                                "jurisdiction": jurisdiction,
                            },
                        }
                    )

        if len(sections) < 5 and "<h3>" in content:
            logger.info(f"Falling back to <h3> splitting for {act_name}")
            sections = []
            parts = re.split(r"<h3>", content)
            preamble = self.clean_html(parts[0])
            if preamble:
                sections.append(
                    {
                        "content": self.build_chunk_text(act_name, "Preamble", preamble),
                        "metadata": {
                            "act_name": act_name,
                            "section": "Preamble",
                            "doc_type": doc_type,
                            "jurisdiction": jurisdiction,
                        },
                    }
                )
            for part in parts[1:]:
                full_part = "<h3>" + part
                sec_num = self.extract_sec_num(full_part)
                clean_content = self.clean_html(full_part)
                if clean_content:
                    sections.append(
                        {
                            "content": self.build_chunk_text(act_name, sec_num, clean_content),
                            "metadata": {
                                "act_name": act_name,
                                "section": sec_num,
                                "doc_type": doc_type,
                                "jurisdiction": jurisdiction,
                            },
                        }
                    )

        if len(sections) < 5:
            logger.info(f"Falling back to Plain Text regex for {act_name}")
            sections = []
            section_pattern = r"\n(?:\s*Section\s+)?(\d+[A-Z]?)\.\s+"
            parts = re.split(section_pattern, "\n" + content)
            if parts[0].strip():
                sections.append(
                    {
                        "content": self.build_chunk_text(act_name, "Preamble", parts[0].strip()),
                        "metadata": {
                            "act_name": act_name,
                            "section": "Preamble",
                            "doc_type": doc_type,
                            "jurisdiction": jurisdiction,
                        },
                    }
                )
            for i in range(1, len(parts), 2):
                sections.append(
                    {
                        "content": self.build_chunk_text(act_name, parts[i], parts[i + 1].strip()),
                        "metadata": {
                            "act_name": act_name,
                            "section": parts[i],
                            "doc_type": doc_type,
                            "jurisdiction": jurisdiction,
                        },
                    }
                )

        for sec in sections:
            sec["metadata"]["doc_type"] = doc_type
            sec["metadata"]["jurisdiction"] = jurisdiction
            if "act_name" not in sec["metadata"]:
                sec["metadata"]["act_name"] = act_name

        return sections

    def extract_result_tid(self, result: Dict[str, Any]) -> Optional[int]:
        for key in ("tid", "doc_id", "id"):
            value = result.get(key)
            if value is None:
                continue
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
        return None

    def score_search_result(self, result: Dict[str, Any], act: Dict[str, Any]) -> int:
        title = result.get("title") or result.get("headline") or result.get("doc_title") or result.get("name") or ""
        normalized_title = normalize_legal_title(title)
        candidates = [act["name"], *act.get("aliases", [])]
        normalized_candidates = [normalize_legal_title(item) for item in candidates]
        query_tokens = set(normalize_legal_title(act.get("search_query") or act["name"]).split())

        score = 0
        if normalized_title in normalized_candidates:
            score += 100
        if any(candidate in normalized_title for candidate in normalized_candidates):
            score += 40
        if query_tokens and query_tokens.issubset(set(normalized_title.split())):
            score += 20
        if " vs " not in normalized_title and " v " not in normalized_title:
            score += 10
        if act.get("doc_type") == "rule" and "rule" in normalized_title:
            score += 10
        if act.get("doc_type") == "statute" and "act" in normalized_title:
            score += 10
        return score

    async def resolve_tid_from_search(self, act: Dict[str, Any]) -> Optional[int]:
        query = act.get("search_query") or act["name"]
        logger.info(f"Resolving document id for {act['name']} using query: {query}")
        results = await self.client.search(IndianKanoonQueryBuilder(query))
        if not results:
            return None

        ranked = sorted(results, key=lambda result: self.score_search_result(result, act), reverse=True)
        for result in ranked:
            tid = self.extract_result_tid(result)
            if tid:
                return tid
        return None

    async def ingest_entry(self, act: Dict[str, Any]) -> None:
        act_display_name = act["name"]
        tid = act.get("tid") or await self.resolve_tid_from_search(act)
        if not tid:
            logger.error(f"Could not resolve Indian Kanoon id for {act_display_name}")
            return

        logger.info(f"==> Ingesting: {act_display_name} (TID: {tid})")
        doc_data = await self.client.doc(str(tid))
        content = doc_data.get("doc") or doc_data.get("content")
        if not content:
            logger.warning(f"No content returned for {act_display_name}")
            return

        chunks = self.chunk_by_sections(
            content,
            act_display_name,
            doc_type=act.get("doc_type", "statute"),
            jurisdiction=act.get("jurisdiction", "India"),
        )
        logger.info(f"Split into {len(chunks)} sections.")
        if chunks:
            for chunk in chunks:
                chunk.update(
                    {
                        "title": act_display_name,
                        "source": "IndianKanoon",
                        "doc_id": str(tid),
                        "url": f"https://indiankanoon.org/doc/{tid}/",
                    }
                )
            self.store.add_documents(chunks, content_key="content")
            self.update_tracking(act, len(chunks))

    def update_tracking(self, act: Dict[str, Any], count: int) -> None:
        if not os.path.exists(self.tracking_file):
            return

        with open(self.tracking_file, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")

        act_name = act["name"]
        date_str = datetime.now().strftime("%Y-%m-%d")
        replacement_line = (
            f"| {act_name} | Ingested | {count} sections | {date_str} | "
            f"{act.get('priority', 'Priority 1')} | {act.get('notes', '')} |"
        )

        new_lines = []
        replaced = False
        for line in lines:
            if act_name in line:
                new_lines.append(replacement_line)
                replaced = True
            else:
                new_lines.append(line)

        if not replaced:
            insertion_header = "## Procedural Rules" if act.get("doc_type") == "rule" else "## Core Statutes (Bare Acts)"
            final_lines = []
            inserted = False
            for index, line in enumerate(new_lines):
                final_lines.append(line)
                if (
                    not inserted
                    and index > 0
                    and new_lines[index - 1].strip() == insertion_header
                    and line.startswith("| :---")
                ):
                    final_lines.append(replacement_line)
                    inserted = True
            new_lines = final_lines

        with open(self.tracking_file, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk-ingest curated statutes and procedural rules into the legal research vector store.")
    parser.add_argument(
        "--only",
        help="Comma-separated list of act names or aliases to ingest. Example: \"Indian Evidence Act, Limitation Act\"",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the curated ingestion list without making Indian Kanoon requests.",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    acts = get_legal_research_act_catalog()
    if args.only:
        requested_names = [item.strip() for item in args.only.split(",") if item.strip()]
        acts, unresolved = match_catalog_entries(requested_names)
        if unresolved:
            logger.warning(f"Unresolved act names skipped: {', '.join(unresolved)}")

    if args.dry_run:
        for act in acts:
            logger.info(
                f"Catalog entry: {act['name']} | type={act.get('doc_type')} | priority={act.get('priority')} | tid={act.get('tid', 'search')}"
            )
        return

    ingestor = LegalCorpusIngestor()
    for act in acts:
        try:
            await ingestor.ingest_entry(act)
        except Exception as exc:
            logger.error(f"Failed {act['name']}: {exc}")
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())
