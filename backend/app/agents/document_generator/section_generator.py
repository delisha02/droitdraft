from typing import List, Dict, Any

from app.services.llm_service import llm_service

SECTION_SEPARATOR = "\n---section---\n"

async def generate_sections(template: str, case_facts: Dict[str, Any]) -> List[str]:
    """Splits the template into sections and generates each section.

    Args:
        template: The document template.
        case_facts: A dictionary of case facts.

    Returns:
        A list of generated sections.
    """
    sections = template.split(SECTION_SEPARATOR)
    generated_sections = []

    for section_template in sections:
        # Here you could add more complex logic to generate each section,
        # for example, by creating a specific prompt for each section.
        # For now, we will just use the llm_service to fill the template.
        
        generated_section = await llm_service.generate_document(
            case_facts=case_facts,
            template=section_template
        )
        generated_sections.append(generated_section)

    return generated_sections
