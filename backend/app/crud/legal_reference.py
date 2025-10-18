'''
This file contains CRUD operations for the LegalReference model.
'''

from app.crud.base import CRUDBase
from app.models.models import LegalReference
from app.schemas.legal_reference import LegalReferenceCreate, LegalReferenceUpdate


class CRUDLegalReference(CRUDBase[LegalReference, LegalReferenceCreate, LegalReferenceUpdate]):
    pass


legal_reference = CRUDLegalReference(LegalReference)
