'''
This file contains the Pydantic schemas for the Template model.
'''

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    document_type: str  # e.g., 'notice', 'complaint', 'will'
    jurisdiction: str  # e.g., 'India', 'Maharashtra'
    version: str = "1.0"
    author: Optional[str] = None
    is_active: bool = True


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    is_active: Optional[bool] = None


class TemplateInDBBase(TemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0

    class Config:
        from_attributes = True


class Template(TemplateInDBBase):
    pass
