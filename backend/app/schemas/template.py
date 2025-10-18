'''
This file contains the Pydantic schemas for the Template model.
'''

from pydantic import BaseModel


class TemplateBase(BaseModel):
    name: str
    description: str | None = None
    content: str


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(TemplateBase):
    pass


class TemplateInDBBase(TemplateBase):
    id: int

    class Config:
        from_attributes = True


class Template(TemplateInDBBase):
    pass
