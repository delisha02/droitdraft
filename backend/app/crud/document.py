'''
This file contains CRUD operations for the Document model.
'''

from app.crud.base import CRUDBase
from app.models.models import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    pass


document = CRUDDocument(Document)
