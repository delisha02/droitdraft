import spacy
from spacy.language import Language
from typing import List, Dict, Any, Optional

# Load a pre-trained spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model. This will happen only once.")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extracts named entities from a given text using spaCy.
    """
    doc = nlp(text)
    entities = []
    # Extract entities recognized by the loaded model
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "start": ent.start_char,
            "end": ent.end_char,
            "label": ent.label_
        })
    
    # Additionally, extract entities based on dependency parsing or custom logic if needed
    # For instance, to identify specific phrases that might not be NER entities but are important facts
    
    return entities

def add_custom_patterns(nlp: Language, patterns: List[Dict[str, Any]]):
    """
    Adds custom patterns to the spaCy NER pipeline using EntityRuler.
    """
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner") # Add before 'ner' to prioritize custom patterns
    else:
        ruler = nlp.get_pipe("entity_ruler")
    ruler.add_patterns(patterns)

# Example custom patterns for legal entities (to be expanded based on specific needs)
# These patterns can help identify specific roles, document types, or legal concepts
custom_patterns = [
    {"label": "COURT", "pattern": "Supreme Court"},
    {"label": "COURT", "pattern": "High Court"},
    {"label": "LEGAL_ACT", "pattern": [{"LOWER": "maharashtra"}, {"LOWER": "rent"}, {"LOWER": "control"}, {"LOWER": "act"}]},
    {"label": "LEGAL_ACT", "pattern": [{"LOWER": "indian"}, {"LOWER": "penal"}, {"LOWER": "code"}]},
    {"label": "TENANT", "pattern": [{"LOWER": "tenant"}, {"POS": "PROPN"}]},
    {"label": "LANDLORD", "pattern": [{"LOWER": "landlord"}, {"POS": "PROPN"}]},
    {"label": "AMOUNT", "pattern": [{"LIKE_NUM": True}, {"TEXT": {"REGEX": "rupees|rs|INR"}}, {"OP": "?"}]},
    {"label": "DATE_PERIOD", "pattern": [{"LOWER": "since"}, {"POS": "PROPN"}, {"LIKE_NUM": True}]}, # e.g., "since July 2025"
    {"label": "TEMPLATE_NAME", "pattern": [{"LOWER": "legal"}, {"LOWER": "notice"}]} # Simple pattern for template
]

add_custom_patterns(nlp, custom_patterns)