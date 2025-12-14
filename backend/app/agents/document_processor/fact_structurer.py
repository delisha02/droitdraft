from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.case_facts import CaseFact, Party, Claim, TimelineEvent, Evidence

class FactStructurer:
    """
    Structures extracted entities into a CaseFact Pydantic model.
    """

    def __init__(self):
        self.extracted_template_id: Optional[str] = None
        self.extracted_research_query: Optional[str] = None

    def structure_facts(self, extracted_entities: List[Dict[str, Any]], document_id: str, document_type: str) -> CaseFact:
        """
        Groups related entities, creates chronological timelines, links parties,
        associates amounts, and structures claims into a CaseFact.

        Args:
            extracted_entities: A list of dictionaries, where each dictionary represents
                                an extracted entity with its type, text, and other relevant info.
            document_id: Unique identifier for the source document.
            document_type: Type of the source document.

        Returns:
            A CaseFact Pydantic model.
        """
        parties: List[Party] = []
        claims: List[Claim] = []
        timeline: List[TimelineEvent] = []
        evidence: List[Evidence] = []
        
        sender_name: Optional[str] = None
        recipient_name: Optional[str] = None
        issue: Optional[str] = None
        location: Optional[str] = None
        amount: Optional[float] = None
        statute: Optional[str] = None
        event_date: Optional[datetime] = None

        # Process entities
        for entity in extracted_entities:
            entity_label = entity.get("type")
            entity_text = entity.get("text")

            if entity_label == "PERSON":
                # Heuristic: First person encountered could be sender, second recipient. Needs refinement.
                if not sender_name:
                    sender_name = entity_text
                elif not recipient_name:
                    recipient_name = entity_text
                parties.append(Party(name=entity_text, role="UNKNOWN"))
            elif entity_label == "ORGANIZATION":
                parties.append(Party(name=entity_text, role="ORGANIZATION"))
            elif entity_label == "DATE":
                try:
                    # Attempt to parse date in common formats
                    event_date = datetime.fromisoformat(entity_text)
                    timeline.append(TimelineEvent(date=event_date, description=f"Event on {entity_text}"))
                except ValueError:
                    try: # Try parsing from common formats if isoformat fails
                        event_date = datetime.strptime(entity_text, "%B %Y") # e.g., "July 2025"
                        timeline.append(TimelineEvent(date=event_date, description=f"Event on {entity_text}"))
                    except ValueError:
                        pass # Handle other date formats as needed
            elif entity_label == "LEGAL_ACT":
                statute = entity_text
                if not self.extracted_research_query:
                    self.extracted_research_query = entity_text # Use first legal act as research query
            elif entity_label == "GPE": # Geo-Political Entity for location
                location = entity_text
            elif entity_label == "AMOUNT":
                try:
                    # Extract numerical part, assuming it's at the beginning
                    num_str = "".join(filter(str.isdigit, entity_text))
                    amount = float(num_str)
                except ValueError:
                    pass
            elif entity_label == "TENANT":
                recipient_name = entity_text # Override if a specific role is identified
                parties.append(Party(name=entity_text, role="TENANT"))
            elif entity_label == "LANDLORD":
                sender_name = entity_text # Override if a specific role is identified
                parties.append(Party(name=entity_text, role="LANDLORD"))
            elif entity_label == "TEMPLATE_NAME":
                self.extracted_template_id = entity_text # Extract template name

        # Populate issue based on query if possible, or a generic placeholder
        # This part often requires more sophisticated NLP (e.g., LLM for summarization)
        if not issue and document_type == "natural_language_query":
            issue = "Non-payment of rent" if "non-payment of rent" in extracted_entities.__str__().lower() else "General Legal Matter"

        # Create Claim based on available info
        if issue or amount or event_date:
            claims.append(Claim(description=issue or "Claim", amount=amount, date=event_date))


        # Sort timeline events by date
        timeline.sort(key=lambda event: event.date)

        return CaseFact(
            document_id=document_id,
            document_type=document_type,
            parties=parties,
            claims=claims,
            timeline=timeline,
            evidence=evidence,
            sender_name=sender_name,
            recipient_name=recipient_name,
            issue=issue,
            location=location,
            amount=amount,
            statute=statute,
            confidence_score=0.75, # Placeholder confidence score
            metadata={"source_processing": "fact_structurer_v2"}
        )
