from app.agents.legal_research.document_store import _build_chroma_metadata


def test_build_chroma_metadata_flattens_nested_metadata():
    doc = {
        "content": "Section text",
        "metadata": {
            "act_name": "Maharashtra Rent Control Act, 1999",
            "section": "16",
            "doc_type": "statute",
        },
        "title": "Maharashtra Rent Control Act, 1999",
        "source": "IndianKanoon",
    }

    metadata = _build_chroma_metadata(doc)

    assert metadata["act_name"] == "Maharashtra Rent Control Act, 1999"
    assert metadata["section"] == "16"
    assert metadata["doc_type"] == "statute"
    assert metadata["title"] == "Maharashtra Rent Control Act, 1999"
    assert metadata["source"] == "IndianKanoon"
