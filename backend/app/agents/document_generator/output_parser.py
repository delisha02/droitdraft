
import re

def parse_generated_document(llm_output: str) -> str:
    """Parses the LLM output to extract the generated document."""
    
    # Possible markers used in prompt_templates.py or legacy code
    markers = [
        "**Generated Legal Draft:**",
        "**Generated Document:**",
        "Generated Legal Draft:",
        "Generated Document:"
    ]
    
    for marker in markers:
        if marker in llm_output:
            parts = llm_output.split(marker)
            content = parts[-1].strip()
            
            # Use regex to strip common trailing noise (Notes, conclusions, templates references)
            # This handles variations like "---", "Note:", "Note :", "**Note:**", etc. at the end of a block.
            noise_pattern = r"(?:\n+)(?:---|\*{3,}|_{3,}|\*{0,2}Note|Conclusion|This draft is based on|Please note).*$"
            content = re.split(noise_pattern, content, flags=re.IGNORECASE | re.DOTALL)[0].strip()
            
            return content
    
    # Fallback if no marker is found
    # If the output starts with markdown code blocks, try to extract from them
    if "```" in llm_output:
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", llm_output, re.DOTALL)
        if code_blocks:
            return code_blocks[-1].strip()

    return llm_output.strip()
