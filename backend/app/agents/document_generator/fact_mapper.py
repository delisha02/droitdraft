
from typing import Dict, Any

def map_facts_to_template(case_facts: Dict[str, Any], template: str) -> str:
    """Maps extracted case facts to template variables.

    This function replaces placeholders in the format [placeholder] with the corresponding values from the case_facts dictionary.

    Args:
        case_facts: A dictionary containing the case facts.
        template: A string containing the document template with placeholders.

    Returns:
        A string with the placeholders replaced by the case facts.
    """
    
    for key, value in case_facts.items():
        # Support multiple placeholder formats
        placeholders = [f"{{{{ {key} }}}}", f"{{{{{key}}}}}", f"[{key}]"]
        for p in placeholders:
            template = template.replace(p, str(value))
            
    return template
