from typing import Dict, Any
from app.agents.document_generator.llm_client import llm_client

class GhostTypingEngine:
    """
    Predicts the next legal sentence based on current document context and case facts.
    """

    async def suggest_next_sentence(self, current_content: str, case_facts: Dict[str, Any], doc_type: str = None) -> str:
        """
        Generates a contextual suggestion for the next sentence.
        """
        # Clean current content from HTML if necessary, or just use it as context
        # We focus on the last few paragraphs for local context
        
        system_context = "You are a Senior Legal Associate in Maharashtra. You provide concise, professional continuations for legal drafts."
        
        prompt = f"""
{system_context}

**Case Facts:**
{case_facts}

**Current Draft Content (Last part):**
...{current_content[-1000:] if len(current_content) > 1000 else current_content}

**Instructions:**
1. Predict the logical NEXT SENTENCE for this legal document.
2. Ensure it is grounded in the Case Facts provided.
3. Keep it brief (one sentence).
4. Do not include any prefixes like "Suggestion:" or "AI:".
5. If the draft seems complete or no clear continuation exists, return an empty string.

**Next Sentence:**
"""
        suggestion = await llm_client.generate(prompt)
        
        # Clean up suggestion (remove quotes, extra whitespace)
        suggestion = suggestion.strip().strip('"').strip("'")
        
        # If it's too long or has multiple sentences, just take the first one
        if "." in suggestion:
            suggestion = suggestion.split(".")[0] + "."
            
        return suggestion

ghost_typing_engine = GhostTypingEngine()
