import pytest
from app.agents.document_processor.ner_engine import extract_entities

def test_extract_entities():
    """
    Tests the extraction of named entities from a text.
    """
    text = "The Supreme Court of India is the highest judicial court."
    entities = extract_entities(text)
    
    assert len(entities) > 0
    
    # Check for a specific entity
    found_court = False
    for entity in entities:
        if entity["label"] == "COURT" and entity["text"] == "Supreme Court":
            found_court = True
            break
    assert found_court