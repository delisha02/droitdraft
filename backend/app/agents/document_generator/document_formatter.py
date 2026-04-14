import re
from typing import List

INLINE_CLAUSE_HEADINGS = (
    "DECLARATION",
    "EXECUTOR",
    "BENEFICIARIES AND ASSETS",
    "ATTESTATION",
    "PRAYER",
    "FACTUAL BACKGROUND",
    "GRIEVANCE",
    "DEMAND",
    "CAUSE OF ACTION",
    "PROPERTY",
    "CONSIDERATION",
    "POSSESSION",
    "INDEMNITY",
    "FSI/TDR",
    "RERA",
    "CORPUS",
    "ALTERNATE ACCOMMODATION",
)
_INLINE_CLAUSE_HEADINGS_PATTERN = re.compile(
    rf"^(?P<prefix>\s*\d+\.\s+)(?P<label>{'|'.join(re.escape(item) for item in INLINE_CLAUSE_HEADINGS)})\s*:\s*(?P<content>.*)$",
    re.IGNORECASE,
)
_SECTION_HEADINGS_TO_DROP = {"WHEREAS:", "TERMS AND CONDITIONS:", "CORE CLAUSES:", "SCHEDULE OF PROPERTY:"}


def _strip_inline_clause_heading(line: str) -> str:
    match = _INLINE_CLAUSE_HEADINGS_PATTERN.match(line)
    if not match:
        return line
    return f"{match.group('prefix')}{match.group('content').strip()}".rstrip()


def normalize_clause_style(text: str) -> str:
    """Normalizes legacy heading-heavy clause formatting into plain numbered clauses."""
    normalized_lines: list[str] = []
    last_clause_number = 0
    convert_bullets_to_numbers = False

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            normalized_lines.append("")
            convert_bullets_to_numbers = False
            continue

        upper = stripped.upper()
        if upper in _SECTION_HEADINGS_TO_DROP:
            convert_bullets_to_numbers = upper in {"TERMS AND CONDITIONS:", "CORE CLAUSES:"}
            continue

        numbered_match = re.match(r"^(?P<indent>\s*)(?P<number>\d+)\.\s+(?P<content>.*)$", line)
        if numbered_match:
            last_clause_number = int(numbered_match.group("number"))
            convert_bullets_to_numbers = False
            normalized_lines.append(_strip_inline_clause_heading(line))
            continue

        prayer_match = re.match(r"^\s*Prayer:\s*(?P<content>.+)$", line, re.IGNORECASE)
        if prayer_match and last_clause_number:
            last_clause_number += 1
            normalized_lines.append(f"{last_clause_number}. {prayer_match.group('content').strip()}")
            continue

        description_match = re.match(r"^\s*Detailed Description:\s*(?P<content>.+)$", line, re.IGNORECASE)
        if description_match and last_clause_number:
            last_clause_number += 1
            content = description_match.group("content").strip()
            normalized_lines.append(f"{last_clause_number}. The detailed description of the property is {content}")
            continue

        bullet_match = re.match(r"^(?P<indent>\s*)-\s+(?P<content>.*)$", line)
        if bullet_match and convert_bullets_to_numbers and last_clause_number:
            last_clause_number += 1
            bullet_content = bullet_match.group("content").strip()
            bullet_content = re.sub(
                rf"^(?:{'|'.join(re.escape(item) for item in INLINE_CLAUSE_HEADINGS)})\s*:\s*",
                "",
                bullet_content,
                flags=re.IGNORECASE,
            ).strip()
            normalized_lines.append(f"{bullet_match.group('indent')}{last_clause_number}. {bullet_content}")
            continue

        normalized_lines.append(line)
        convert_bullets_to_numbers = False

    normalized_text = "\n".join(normalized_lines)
    normalized_text = re.sub(r"\n{3,}", "\n\n", normalized_text)
    return normalized_text.strip()


def format_document(title: str, sections: List[str]) -> str:
    """Formats the final document."""
    normalized_sections = [normalize_clause_style(section) for section in sections]
    document = f"# {title}\n\n"
    document += "\n\n".join(normalized_sections)
    return normalize_clause_style(document)
