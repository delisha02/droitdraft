
import tiktoken
from typing import Dict, Any

from app.agents.document_generator.llm_client import llm_client
from app.agents.document_generator.prompt_templates import create_generation_prompt
from app.agents.document_generator.output_parser import parse_generated_document

class TokenUsageTracker:
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.total_tokens = 0

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def track(self, text: str):
        self.total_tokens += self.count_tokens(text)

    def get_total_tokens(self) -> int:
        return self.total_tokens

class LLMService:
    def __init__(self):
        self.token_tracker = TokenUsageTracker()

    async def generate_document(
        self, case_facts: Dict[str, Any], template: str, use_groq: bool = True
    ) -> str:
        """Generates a legal document using the LLM."""
        
        prompt = create_generation_prompt(case_facts, template)
        self.token_tracker.track(prompt)  # Track input tokens

        generated_text = await llm_client.generate(prompt, use_groq=use_groq)
        self.token_tracker.track(generated_text)  # Track output tokens

        parsed_document = parse_generated_document(generated_text)
        
        return parsed_document

    def get_token_usage(self) -> int:
        return self.token_tracker.get_total_tokens()

llm_service = LLMService()
