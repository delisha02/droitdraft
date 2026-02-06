'''
This file contains the Pydantic schemas for the Document model.
'''

from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    content: str | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass


class DocumentInDBBase(DocumentBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Document(DocumentInDBBase):
    pass


class DocumentGenerate(BaseModel):
    title: str
    template_id: int
    case_facts: dict


class GhostSuggestRequest(BaseModel):
    current_content: str
    case_facts: dict
    doc_type: str | None = None


class GhostSuggestResponse(BaseModel):
    suggestion: str
