from typing import Dict, Any

from app.agents.document_generator.fact_mapper import map_facts_to_template
from app.agents.document_generator.section_generator import generate_sections, SECTION_SEPARATOR
from app.agents.document_generator.consistency_checker import check_consistency
from app.agents.document_generator.document_formatter import format_document

class DocumentAssemblyEngine:
    async def assemble_document(
        self,
        template: str,
        case_facts: Dict[str, Any],
        title: str
    ) -> str:
        """Assembles a document from a template and case facts.

        Args:
            template: The document template.
            case_facts: A dictionary of case facts.
            title: The title of the document.

        Returns:
            The assembled document as a string.
        """

        # 1. Fact-to-template mapping
        filled_template = map_facts_to_template(case_facts, template)

        # 2. Section-wise generation
        sections = await generate_sections(filled_template, case_facts)

        # 3. Combine sections for consistency check
        combined_sections = "\n".join(sections)

        # 4. Document consistency checking
        consistency_errors = check_consistency(combined_sections)
        if consistency_errors:
            # For now, we'll just raise an exception. 
            # In a real application, you might want to handle this more gracefully.
            raise ValueError(f"Consistency errors found: {', '.join(consistency_errors)}")

        # 5. Final document assembly
        final_document = format_document(title, sections)

        return final_document

assembly_engine = DocumentAssemblyEngine()
