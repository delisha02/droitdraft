import spacy
from spacy.language import Language
from typing import List, Dict, Any

# Create a blank spaCy model. This avoids loading the default model with onnxruntime.
nlp = spacy.blank("en")

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extracts named entities from a given text using spaCy.
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "start": ent.start_char,
            "end": ent.end_char,
            "label": ent.label_
        })
    return entities

def add_custom_patterns(nlp: Language, patterns: List[Dict[str, Any]]):
    """
    Adds custom patterns to the spaCy NER pipeline using EntityRuler.
    """
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler")
    else:
        ruler = nlp.get_pipe("entity_ruler")
    ruler.add_patterns(patterns)

# Example custom patterns (to be expanded)
custom_patterns = [
    {"label": "COURT", "pattern": "Supreme Court"},
    {"label": "COURT", "pattern": "High Court"},
]

add_custom_patterns(nlp, custom_patterns)