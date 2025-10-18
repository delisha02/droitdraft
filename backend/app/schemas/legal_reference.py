'''
This file contains the Pydantic schemas for the LegalReference model.
'''

from pydantic import BaseModel


class LegalReferenceBase(BaseModel):
    text: str
    source: str | None = None


class LegalReferenceCreate(LegalReferenceBase):
    pass


class LegalReferenceUpdate(LegalReferenceBase):
    pass


class LegalReferenceInDBBase(LegalReferenceBase):
    id: int

    class Config:
        from_attributes = True


class LegalReference(LegalReferenceInDBBase):
    pass
