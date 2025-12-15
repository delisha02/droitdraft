
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.models.models import User
from app.schemas.document import Document, DocumentCreate, DocumentUpdate

router = APIRouter()

@router.post("/", response_model=Document)
def create_document(
    *,
    db: Session = Depends(deps.get_db),
    document_in: DocumentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new document.
    """
    document = crud.document.create_with_owner(
        db=db, obj_in=document_in, owner_id=current_user.id
    )
    return document

@router.get("/", response_model=List[Document])
def read_documents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve documents.
    """
    documents = crud.document.get_multi_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return documents

@router.get("/{document_id}", response_model=Document)
def read_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get document by ID.
    """
    document = crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return document

@router.put("/{document_id}", response_model=Document)
def update_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    document_in: DocumentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update document.
    """
    document = crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    document = crud.document.update(db, db_obj=document, obj_in=document_in)
    return document

@router.delete("/{document_id}", response_model=Document)
def delete_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a document.
    """
    document = crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    document = crud.document.remove(db, id=document_id)
    return document
