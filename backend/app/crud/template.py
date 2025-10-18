'''
This file contains CRUD operations for the Template model.
'''

from app.crud.base import CRUDBase
from app.models.models import Template
from app.schemas.template import TemplateCreate, TemplateUpdate


class CRUDTemplate(CRUDBase[Template, TemplateCreate, TemplateUpdate]):
    pass


template = CRUDTemplate(Template)
