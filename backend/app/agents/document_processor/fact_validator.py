from typing import List, Dict, Any
from app.schemas.case_facts import CaseFact
from pydantic import ValidationError

class FactValidator:
    """
    Validates a CaseFact Pydantic model against predefined rules.
    """

    def __init__(self):
        pass

    def validate_facts(self, case_fact: CaseFact) -> List[str]:
        """
        Validates a CaseFact object and returns a list of error messages.

        Args:
            case_fact: The CaseFact Pydantic model to validate.

        Returns:
            A list of strings, where each string is a validation error message.
            Returns an empty list if no errors are found.
        """
        errors: List[str] = []

        # Pydantic's own validation is handled during CaseFact instantiation.
        # Here, we can add custom business logic validation.

        # Example: Check for required fields based on document type
        if case_fact.document_type == "Complaint":
            if not case_fact.claims:
                errors.append("Complaint document type requires at least one claim.")
            if not any(p.role == "Plaintiff" for p in case_fact.parties):
                errors.append("Complaint document type requires at least one Plaintiff party.")

        # Example: Logical consistency checks
        for claim in case_fact.claims:
            if claim.claimant_id and not any(p.name == claim.claimant_id for p in case_fact.parties):
                errors.append(f"Claimant ID '{claim.claimant_id}' for claim '{claim.description}' does not match any existing party.")

        # Example: Completeness assessment (e.g., flag if critical info is missing)
        if not case_fact.parties:
            errors.append("No parties found in the case fact.")
        if not case_fact.timeline:
            errors.append("No timeline events found in the case fact.")

        return errors

    def validate_schema(self, data: Dict[str, Any]) -> List[str]:
        """
        Validates raw data against the CaseFact Pydantic schema.

        Args:
            data: A dictionary representing the raw data to validate.

        Returns:
            A list of strings, where each string is a validation error message.
            Returns an empty list if no errors are found.
        """
        errors: List[str] = []
        try:
            CaseFact(**data)
        except ValidationError as e:
            for error in e.errors():
                errors.append(f"{error['loc'][0]}: {error['msg']}")
        return errors
