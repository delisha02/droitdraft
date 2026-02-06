import logging
from typing import List, Dict, Any, Optional

from app.agents.legal_research.document_store import DocumentStore
from app.agents.document_generator.llm_client import llm_client
from app.agents.legal_research.retrievers import get_persistent_retriever

logger = logging.getLogger(__name__)

class LegalResearchAgent:
    """
    An agent that performs legal research using a persistent vector store (RAG).
    """

    def __init__(self, persist_directory: str = "chroma_db"):
        self.store = DocumentStore(persist_directory=persist_directory)
        self.retriever = get_persistent_retriever(persist_directory=persist_directory)

    async def answer_query(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Answers a legal research query by retrieving context and generating a response.
        """
        try:
            logger.info(f"Researching query: {query}")
            
            # 1. Retrieve relevant documents
            # We use the retriever for similarity search
            docs = self.retriever.invoke(query)
            
            if not docs:
                return {
                    "answer": "I couldn't find any specific legal documents in my database related to your query.",
                    "sources": []
                }

            # 2. Construct Context
            context_parts = []
            sources = []
            for i, doc in enumerate(docs[:k]):
                content = doc.page_content
                metadata = doc.metadata
                source_info = f"Source {i+1}: {metadata.get('title', 'Unknown Title')} (Source: {metadata.get('source', 'Unknown')})"
                if metadata.get('url'):
                    source_info += f" - {metadata.get('url')}"
                
                context_parts.append(f"--- {source_info} ---\n{content}\n")
                sources.append({
                    "title": metadata.get('title'),
                    "url": metadata.get('url'),
                    "source": metadata.get('source'),
                    "id": metadata.get('doc_id') or metadata.get('tid')
                })

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
