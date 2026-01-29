import json
from typing import Dict, Any, List, Optional
from app.agents.document_generator.llm_client import llm_client
from app.schemas.case_facts import CaseFact, Party, Claim, TimelineEvent

class LLMExtractor:
    """
    Upgraded Extraction Engine using LLMs to extract structured facts from raw text.
    Replaces the traditional spaCy-based NER with robust reasoning.
    """

    SYSTEM_PROMPT = """
    You are a specialized Legal Document Processing Assistant. Your task is to extract critical legal facts from the provided text.
    The text may be from a Will, a Death Certificate, a Sale Deed, or other legal documents.
    
    Extract the following information if present:
    1. Parties involved (Names, Roles like Testator, Executor, Buyer, Seller, etc., and Addresses).
    2. Critical Dates (Date of death, date of execution, date of notice).
    3. Locations (Property address, place of death).
    4. Amounts (Sale price, corpus fund, etc.).
    5. Specific Claims or Clauses.

    IMPORTANT: Return the output ALWAYS in valid JSON format following this exact structure:
    {
      "parties": [{"name": "string", "role": "string", "address": "string"}],
      "claims": [{"description": "string", "amount": number}],
      "timeline": [{"date": "YYYY-MM-DD", "description": "string"}],
      "location": "string",
      "summary": "Brief summary of the document"
    }
    
    If a field is not found, return an empty list or null for that field. Do not make up information.
    """

    async def extract(self, text: str) -> Dict[str, Any]:
        """
        Processes text and returns structured facts as a dictionary.
        """
        prompt = f"{self.SYSTEM_PROMPT}\n\nDOCUMENT TEXT:\n{text}\n\nEXTRACTED JSON:"
        
        try:
            # Using LLM (Groq prioritized)
            response_text = await llm_client.generate(prompt, use_groq=True)
            # Robust JSON extraction using regex
            import re
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # Fallback to the old cleaning method if regex fails
                json_str = response_text.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
            
            extracted_data = json.loads(json_str)
            return extracted_data
        except Exception as e:
            import traceback
            print(f"LLM Extraction failed: {e}")
            traceback.print_exc()
            return {
                "parties": [],
                "claims": [],
                "timeline": [],
                "location": None,
                "summary": "Failed to extract facts due to an error."
            }

llm_extractor = LLMExtractor()
