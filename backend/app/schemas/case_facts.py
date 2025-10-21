from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class Party(BaseModel):
    name: str = Field(..., description="Full name of the party")
    role: Optional[str] = Field(None, description="Role of the party (e.g., 'Plaintiff', 'Defendant', 'Testator')")
    address: Optional[str] = Field(None, description="Address of the party")
    contact: Optional[str] = Field(None, description="Contact information (e.g., email, phone)")
    metadata: Dict[str, Any] = Field({}, description="Flexible metadata for the party")

class Claim(BaseModel):
    description: str = Field(..., description="Description of the claim or allegation")
    claimant_id: Optional[str] = Field(None, description="ID of the party making the claim")
    respondent_id: Optional[str] = Field(None, description="ID of the party responding to the claim")
    amount: Optional[float] = Field(None, description="Monetary amount associated with the claim")
    currency: Optional[str] = Field(None, description="Currency of the amount (e.g., 'USD', 'EUR')")
    status: Optional[str] = Field(None, description="Status of the claim (e.g., 'Filed', 'Pending', 'Resolved')")
    metadata: Dict[str, Any] = Field({}, description="Flexible metadata for the claim")

class TimelineEvent(BaseModel):
    date: datetime = Field(..., description="Date and time of the event")
    description: str = Field(..., description="Description of the event")
    event_type: Optional[str] = Field(None, description="Type of event (e.g., 'Filing', 'Hearing', 'Decision')")
    related_parties: List[str] = Field([], description="List of party IDs related to this event")
    metadata: Dict[str, Any] = Field({}, description="Flexible metadata for the event")

class Evidence(BaseModel):
    description: str = Field(..., description="Description of the evidence")
    evidence_type: Optional[str] = Field(None, description="Type of evidence (e.g., 'Document', 'Testimony', 'Exhibit')")
    date: Optional[datetime] = Field(None, description="Date associated with the evidence")
    related_claims: List[str] = Field([], description="List of claim IDs related to this evidence")
    metadata: Dict[str, Any] = Field({}, description="Flexible metadata for the evidence")

class CaseFact(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the source document")
    document_type: str = Field(..., description="Type of the source document (e.g., 'Notice', 'Complaint', 'Will')")
    parties: List[Party] = Field([], description="List of parties involved in the case")
    claims: List[Claim] = Field([], description="List of claims or allegations")
    timeline: List[TimelineEvent] = Field([], description="Chronological list of events")
    evidence: List[Evidence] = Field([], description="List of evidence related to the case")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the facts were extracted")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence score of the extraction (0.0-1.0)")
    metadata: Dict[str, Any] = Field({}, description="Flexible metadata for the entire case fact structure")

    @validator('timeline')
    def sort_timeline(cls, v):
        return sorted(v, key=lambda event: event.date)

    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('Confidence score must be between 0.0 and 1.0')
        return v
