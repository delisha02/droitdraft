import pytest
from datetime import datetime
from app.schemas.case_facts import CaseFact, Party, Claim, TimelineEvent
from app.agents.document_processor.fact_structurer import FactStructurer
from app.agents.document_processor.fact_validator import FactValidator
from app.agents.document_processor.entity_resolver import EntityResolver

# --- Tests for FactStructurer ---

@pytest.fixture
def fact_structurer():
    return FactStructurer()

def test_fact_structurer_basic_structuring(fact_structurer):
    extracted_entities = [
        {"type": "PERSON", "text": "John Doe"},
        {"type": "DATE", "text": "2023-01-15"},
        {"type": "ORGANIZATION", "text": "Acme Corp"},
    ]
    document_id = "doc123"
    document_type = "Complaint"

    case_fact = fact_structurer.structure_facts(extracted_entities, document_id, document_type)

    assert isinstance(case_fact, CaseFact)
    assert case_fact.document_id == document_id
    assert case_fact.document_type == document_type
    assert len(case_fact.parties) == 2
    assert any(p.name == "John Doe" for p in case_fact.parties)
    assert any(p.name == "Acme Corp" for p in case_fact.parties)
    assert len(case_fact.timeline) == 1
    assert case_fact.timeline[0].date.year == 2023
    assert case_fact.confidence_score == 0.75

def test_fact_structurer_empty_entities(fact_structurer):
    extracted_entities = []
    document_id = "doc456"
    document_type = "Will"

    case_fact = fact_structurer.structure_facts(extracted_entities, document_id, document_type)

    assert isinstance(case_fact, CaseFact)
    assert case_fact.document_id == document_id
    assert case_fact.document_type == document_type
    assert not case_fact.parties
    assert not case_fact.claims
    assert not case_fact.timeline
    assert not case_fact.evidence

# --- Tests for FactValidator ---

@pytest.fixture
def fact_validator():
    return FactValidator()

def test_fact_validator_valid_case_fact(fact_validator):
    party = Party(name="Jane Doe", role="Plaintiff")
    claim = Claim(description="Breach of contract", claimant_id="Jane Doe")
    event = TimelineEvent(date=datetime(2023, 1, 1), description="Contract signed")
    
    case_fact = CaseFact(
        document_id="doc789",
        document_type="Complaint",
        parties=[party],
        claims=[claim],
        timeline=[event]
    )
    errors = fact_validator.validate_facts(case_fact)
    assert not errors

def test_fact_validator_invalid_complaint_missing_claim(fact_validator):
    party = Party(name="Jane Doe", role="Plaintiff")
    case_fact = CaseFact(
        document_id="doc789",
        document_type="Complaint",
        parties=[party]
    )
    errors = fact_validator.validate_facts(case_fact)
    assert "Complaint document type requires at least one claim." in errors

def test_fact_validator_invalid_complaint_missing_plaintiff(fact_validator):
    party = Party(name="John Doe", role="Defendant")
    claim = Claim(description="Breach of contract", claimant_id="John Doe")
    case_fact = CaseFact(
        document_id="doc789",
        document_type="Complaint",
        parties=[party],
        claims=[claim]
    )
    errors = fact_validator.validate_facts(case_fact)
    assert "Complaint document type requires at least one Plaintiff party." in errors

def test_fact_validator_schema_validation_errors(fact_validator):
    invalid_data = {
        "document_id": "doc101",
        "document_type": "Notice",
        "confidence_score": 1.5 # Invalid score
    }
    errors = fact_validator.validate_schema(invalid_data)
    assert "confidence_score: Input should be less than or equal to 1" in errors[0]

# --- Tests for EntityResolver ---

@pytest.fixture
def entity_resolver():
    return EntityResolver()

def test_entity_resolver_basic_passthrough(entity_resolver):
    entities = [
        {"type": "PERSON", "text": "Mr. Smith"},
        {"type": "PRONOUN", "text": "he"}
    ]
    document_text = "Mr. Smith said he would arrive soon."
    resolved_entities = entity_resolver.resolve_entities(entities, document_text)
    assert resolved_entities == entities # Placeholder, as current resolver just passes through
