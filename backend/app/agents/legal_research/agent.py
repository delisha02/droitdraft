import logging
import re
from html import unescape
from typing import List, Dict, Any, Optional

from app.agents.document_generator.llm_client import llm_client
from app.services.legal_corpus_catalog import get_legal_research_act_catalog, normalize_legal_title
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)
RESEARCH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "for", "from", "how", "in", "is",
    "it", "of", "on", "or", "that", "the", "to", "under", "what", "when", "which",
    "with", "claim", "essential", "ingredients",
}
SUBSTANTIVE_QUERY_TERMS = {
    "act", "section", "sections", "rule", "rules", "eviction", "arrears", "recovery",
    "grounds", "injunction", "specific", "performance", "dishonour", "cheque",
    "limitation", "partnership", "company", "companies", "rent", "tenant", "landlord",
}

class LegalResearchAgent:
    """
    An agent that performs legal research using a persistent vector store (RAG).
    """

    def __init__(self, persist_directory: str = "chroma_db"):
        self.retrieval_service = RetrievalService(persist_directory=persist_directory)

    def _normalize_content(self, raw_content: str) -> str:
        content = re.sub(r"<[^>]+>", " ", raw_content or "")
        content = unescape(content)
        content = re.sub(r"\s+", " ", content).strip()
        return content.encode("ascii", errors="ignore").decode("ascii")

    def _extract_query_terms(self, query: str) -> List[str]:
        tokens = re.findall(r"[a-z0-9]+", query.lower())
        return [token for token in tokens if token not in RESEARCH_STOPWORDS and len(token) > 2]

    def _select_retrieval_strategy(self, query: str) -> str:
        query_terms = set(self._extract_query_terms(query))
        if query_terms.intersection(SUBSTANTIVE_QUERY_TERMS) or len(query_terms) > 6:
            return "hybrid"
        return "dense"

    def _match_act_from_query(self, query: str) -> Optional[Dict[str, Any]]:
        normalized_query = normalize_legal_title(query)
        for entry in get_legal_research_act_catalog():
            candidates = [entry["name"], *entry.get("aliases", [])]
            normalized_candidates = [normalize_legal_title(candidate) for candidate in candidates]
            if any(candidate in normalized_query for candidate in normalized_candidates):
                return entry
        return None

    def _build_focus_queries(self, query: str) -> List[str]:
        focus_queries = [query]
        act_entry = self._match_act_from_query(query)
        section_refs = re.findall(r"\bsection\s+(\d+[A-Z]?)\b", query, flags=re.IGNORECASE)

        if act_entry:
            focus_queries.append(act_entry["name"])
            if section_refs:
                for section in section_refs:
                    focus_queries.append(f"{act_entry['name']} Section {section}")

            substantive_terms = [
                term for term in self._extract_query_terms(query)
                if term not in normalize_legal_title(act_entry["name"]).split()
            ]
            if substantive_terms:
                focus_queries.append(f"{act_entry['name']} {' '.join(substantive_terms[:6])}")

        deduped_queries: List[str] = []
        seen_queries = set()
        for item in focus_queries:
            key = item.strip().lower()
            if not key or key in seen_queries:
                continue
            deduped_queries.append(item.strip())
            seen_queries.add(key)
        return deduped_queries

    def _score_doc_relevance(self, query_terms: List[str], doc: Any) -> int:
        metadata = getattr(doc, "metadata", {}) or {}
        normalized_content = self._normalize_content(getattr(doc, "page_content", "")).lower()

        score = 0
        for term in query_terms:
            if term in normalized_content:
                score += 5
            if term in str(metadata.get("act_name", "")).lower():
                score += 8
            if term in str(metadata.get("title", "")).lower():
                score += 6
            if term == str(metadata.get("section", "")).lower():
                score += 4

        if metadata.get("section") == "Preamble":
            score -= 8
        if "short title" in normalized_content and "eviction" not in normalized_content and "arrears" not in normalized_content:
            score -= 4
        if normalized_content.startswith("an act to"):
            score -= 4
        return score

    def _rerank_docs(self, query: str, docs: List[Any], k: int) -> List[Any]:
        query_terms = self._extract_query_terms(query)
        ranked_docs = sorted(
            docs,
            key=lambda doc: self._score_doc_relevance(query_terms, doc),
            reverse=True,
        )
        return ranked_docs[:k]

    def _dedupe_docs(self, docs: List[Any]) -> List[Any]:
        seen = set()
        unique_docs = []
        for doc in docs:
            key = (getattr(doc, "page_content", ""), str(getattr(doc, "metadata", {})))
            if key in seen:
                continue
            seen.add(key)
            unique_docs.append(doc)
        return unique_docs

    async def answer_query(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Answers a legal research query by retrieving context and generating a response.
        """
        try:
            logger.info(f"Researching query: {query}")

            strategy = self._select_retrieval_strategy(query)
            docs = []
            for focus_query in self._build_focus_queries(query):
                docs.extend(
                    self.retrieval_service.retrieve_documents(
                        query=focus_query,
                        strategy=strategy,
                        k=max(k, 8),
                    )
                )
            docs = self._dedupe_docs(docs)
            docs = self._rerank_docs(query, docs, k=k)
            
            if not docs:
                return {
                    "answer": "I couldn't find any specific legal documents in my database related to your query.",
                    "sources": []
                }

            # 2. Construct Context with dynamic sizing
            # Groq's Llama 3.3 has 128K token context (~512K chars)
            # We use ~80K chars to leave room for prompt + response
            MAX_CONTEXT_CHARS = 80000
            MAX_CHARS_PER_DOC = 4000  # Allow substantial content per doc
            
            context_parts = []
            sources = []
            total_chars = 0
            
            for i, doc in enumerate(docs[:k]):
                raw_content = doc.page_content
                content = self._normalize_content(raw_content)
                
                # Calculate how much space we have left
                remaining = MAX_CONTEXT_CHARS - total_chars
                if remaining <= 500:  # Stop if not enough room
                    break
                    
                # Truncate this doc to fit (but max 4000 chars per doc)
                allowed = min(MAX_CHARS_PER_DOC, remaining - 200)  # Leave room for header
                content = content[:allowed]
                
                metadata = doc.metadata
                source_title = metadata.get("title") or metadata.get("act_name") or "Unknown Title"
                if metadata.get("section"):
                    source_title = f"{source_title} - Section {metadata.get('section')}"
                source_label = metadata.get("source") or metadata.get("doc_type") or "Unknown"
                source_info = f"Source {i+1}: {source_title} (Source: {source_label})"
                if metadata.get('url'):
                    source_info += f" - {metadata.get('url')}"
                
                doc_text = f"--- {source_info} ---\n{content}\n"
                context_parts.append(doc_text)
                total_chars += len(doc_text)
                
                sources.append({
                    "title": metadata.get('title'),
                    "url": metadata.get('url'),
                    "source": metadata.get('source'),
                    "id": metadata.get('doc_id') or metadata.get('tid')
                })
            
            logger.info(f"Research context: {len(sources)} docs, {total_chars} chars")
            context_str = "\n".join(context_parts)


            # 3. Generate Answer
            prompt = f"""
You are a highly skilled Legal Research Assistant for DroitDraft, specializing in Indian Law. 
Your task is to provide detailed, accurate, and grounded answers to legal queries based ONLY on the provided context.

Context:
{context_str}

User Query: {query}

Instructions:
1. Use the provided context to answer the user's query as comprehensively as possible.
2. If the answer is not in the context, state that you don't have enough information in your specialized database.
2a. If the retrieved context is only generic material like a preamble, short title, or commencement clause, say that the relevant operative provisions were not retrieved.
3. **Citations (CRITICAL)**: Cite your sources naturally within the text. 
   - DO NOT use "Source 1", "Source 2", etc.
   - Use the actual Act name and Section if available (e.g., "Section 10 of the Indian Contract Act, 1872").
   - Use the Case Name and Reporter if it's a judgment (e.g., "*State of Maharashtra v. XYZ*, AIR 2023 SC 456").
4. Maintain a professional and objective legal tone.
5. Provide a summary of the relevant legal principles or rulings found in the context.

Answer:
"""
            answer = await llm_client.generate(prompt)

            return {
                "answer": answer,
                "sources": sources
            }

        except Exception as e:
            logger.error(f"Error in LegalResearchAgent: {e}", exc_info=True)
            return {
                "answer": f"I encountered an error while performing research: {str(e)}",
                "sources": []
            }
