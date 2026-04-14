from app.services.legal_corpus_catalog import match_catalog_entries, normalize_legal_title


def test_normalize_legal_title_handles_spacing_and_punctuation():
    assert normalize_legal_title("High Court Original-Side Rule") == "high court original side rule"


def test_match_catalog_entries_resolves_aliases_and_typos():
    selected, unresolved = match_catalog_entries(
        [
            "Maharashtra rent control act",
            "Indian evidence",
            "Core of civil prodecure",
            "High court original side rule",
            "Labour act",
        ]
    )

    selected_names = {entry["name"] for entry in selected}

    assert "Maharashtra Rent Control Act, 1999" in selected_names
    assert "Indian Evidence Act, 1872" in selected_names
    assert "Code of Civil Procedure, 1908" in selected_names
    assert "Bombay High Court (Original Side) Rules" in selected_names
    assert "Industrial Disputes Act, 1947" in selected_names
    assert unresolved == []
