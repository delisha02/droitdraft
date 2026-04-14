import json
from typing import Dict, Any

DEFAULT_SYSTEM_PROMPT = """
You are a highly skilled Senior Legal Associate specializing in Indian Law (specifically Maharashtra jurisdiction). 
Your task is to draft or refine legal documents based on high-level goals provided by a lawyer/paralegal.

CORE PRINCIPLES:
1. **Fact Grounding**: Prioritize facts extracted from the "Source Evidence" (certificates, IDs, invoices) over generic instructions.
2. **Legal Precision**: Use formal legal terminology suitable for Indian courts.
3. **Natural Citations**: Integrate citations of relevant Sections and Acts directly into the draft (e.g., "pursuant to Section 4 of the Indian Evidence Act, 1872").
4. **Autonomous Drafting**: If the user provides high-level goals (e.g., "Draft a Probate Petition"), use the provided template as a structure but autonomously populate all necessary sections using the evidence.
5. **Consistency**: Ensure names, dates, and amounts are consistent across the entire document.
6. **No Hallucinations**: If critical information (like a date of death) is missing from both the facts and evidence, use a placeholder like `{{ date_of_death }}` rather than guessing.
7. **Clause Style**: Keep the body in plain numbered clauses. Do not use inline clause labels such as `FACTUAL BACKGROUND:`, `GRIEVANCE:`, `DEMAND:`, `CAUSE OF ACTION:`, `DECLARATION:`, or similar heading text inside numbered points.
"""

def create_generation_prompt(case_facts: Dict[str, Any], template: str) -> str:
    """Creates a prompt for the LLM to generate a legal document."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Format facts more intelligently
    facts_lines = []
    for key, value in case_facts.items():
        if key == "file_ids": continue # Skip raw IDs
        if key == "evidence_text": continue # Handle separately
        if key == "retrieved_legal_context": continue # Handle separately
        if key == "retrieved_legal_sources": continue # Handle separately
        
        if isinstance(value, list):
            facts_lines.append(f"**{key.replace('_', ' ').title()}:**")
            for item in value:
                if isinstance(item, dict):
                    item_str = ", ".join([f"{k}: {v}" for k, v in item.items() if v])
                    facts_lines.append(f"  - {item_str}")
                else:
                    facts_lines.append(f"  - {item}")
        elif isinstance(value, dict):
             facts_lines.append(f"**{key.replace('_', ' ').title()}:** {json.dumps(value)}")
        else:
            facts_lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
    
    facts_str = "\n".join(facts_lines)
    
    evidence_section = ""
    if case_facts.get("evidence_text"):
        evidence_section = f"\n**Source Evidence (Grounded Information):**\n{case_facts['evidence_text']}\n"

    legal_context_section = ""
    if case_facts.get("retrieved_legal_context"):
        legal_context_section = f"\n**Grounded Legal Context (Retrieved):**\n{case_facts['retrieved_legal_context']}\n"

    # Extract specific user query if exists
    user_query = case_facts.get("query") or case_facts.get("user_query") or case_facts.get("instructions")
    user_query_section = ""
    if user_query:
        user_query_section = f"\n**Specific User Request:**\n> {user_query}\n"

    prompt = f"""
{DEFAULT_SYSTEM_PROMPT}

**Case Facts & Data Points:**
{facts_str}
{evidence_section}
{legal_context_section}
{user_query_section}

**Legal Template (Structural Blueprint):**
```
{template}
```

**CRITICAL INSTRUCTIONS:**
1. **Prioritize the User Request**: If the user provided a specific query (above), ensure the drafted document directly addresses it.
2. **Handle the Blueprint with Care**: 
   - **Do Not Rewrite standard legal headers or formal structure** unless specifically asked.
   - **Fill all placeholders** like `{{ field_name }}` using the extracted facts, evidence, or user instructions.
   - If a placeholder has no data, use the specific placeholder name: `{{ missing_field }}`.
3. **Evidence-First**: If facts found in Source Evidence (e.g., Death Certificate) conflict with the user's initial prompt, use the Evidence.
4. **Drafting Style**: Ensure the tone is formal, consistent with Maharashtra legal practice. Use "The Vendor", "The Executrix", etc., as appropriate for the document type.
   - Use simple numbered clauses like `1. ...`, `2. ...`, `3. ...`.
   - If the blueprint contains heading-style labels inside clauses, convert them into ordinary sentence text rather than reproducing the label.
5. **No Hallucinations**: Do not invent properties, names, or dates.

**Generated Legal Draft:**
"""
    logger.info(f"[Step 7] Prompt assembled for LLM. Prompt preview: {prompt[:300]}...")
    return prompt
