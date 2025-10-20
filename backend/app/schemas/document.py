'''
This file contains the Pydantic schemas for the Document model.
'''

from pydantic import BaseModel
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    content: str | None = None


class DocumentCreate(DocumentBase):
    owner_id: int


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
