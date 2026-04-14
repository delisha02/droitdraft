from app.agents.document_generator.document_formatter import format_document, normalize_clause_style


def test_normalize_clause_style_removes_inline_numbered_headings():
    source = (
        "1. FACTUAL BACKGROUND: The tenant has defaulted in rent.\n"
        "2. GRIEVANCE: The breach continues despite reminders.\n"
        "3. DEMAND: Pay the arrears within 15 days."
    )

    normalized = normalize_clause_style(source)

    assert "FACTUAL BACKGROUND:" not in normalized
    assert "GRIEVANCE:" not in normalized
    assert "DEMAND:" not in normalized
    assert "1. The tenant has defaulted in rent." in normalized
    assert "2. The breach continues despite reminders." in normalized
    assert "3. Pay the arrears within 15 days." in normalized


def test_normalize_clause_style_converts_legacy_sections_to_numbered_clauses():
    source = (
        "1. The First Party is the lawful owner.\n"
        "2. The Second Party has agreed to redevelop the property.\n\n"
        "CORE CLAUSES:\n"
        "- FSI/TDR: The Developer shall utilize the base FSI.\n"
        "- RERA: The Developer shall register the project under MahaRERA.\n\n"
        "Prayer: Letters of Administration may be granted."
    )

    normalized = normalize_clause_style(source)

    assert "CORE CLAUSES:" not in normalized
    assert "FSI/TDR:" not in normalized
    assert "RERA:" not in normalized
    assert "3. The Developer shall utilize the base FSI." in normalized
    assert "4. The Developer shall register the project under MahaRERA." in normalized
    assert "5. Letters of Administration may be granted." in normalized


def test_format_document_applies_clause_normalization():
    document = format_document(
        "Legal Notice",
        ["1. FACTUAL BACKGROUND: Default in payment.\n2. CAUSE OF ACTION: Proceedings will follow."],
    )

    assert document.startswith("# Legal Notice")
    assert "FACTUAL BACKGROUND:" not in document
    assert "CAUSE OF ACTION:" not in document
