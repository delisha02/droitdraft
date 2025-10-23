from typing import Dict, Any

DEFAULT_SYSTEM_PROMPT = """
You are a highly skilled legal assistant. Your task is to generate a legal document based on the provided case facts and a template. 
Ensure the document is well-structured, uses appropriate legal terminology, and is consistent with the provided facts.
Pay close attention to the placeholders in the template and fill them accurately with the information from the case facts.
Do not add any information that is not present in the case facts.
"""

def create_generation_prompt(case_facts: Dict[str, Any], template: str) -> str:
    """Creates a prompt for the LLM to generate a legal document."""
    
    facts_str = "\n".join([f"- {key.replace('_', ' ').title()}: {value}" for key, value in case_facts.items()])
    
    prompt = f"""
{DEFAULT_SYSTEM_PROMPT}

**Case Facts:**
{facts_str}

**Document Template:**
```
{template}
```

**Generated Document:**
"""
    return prompt
