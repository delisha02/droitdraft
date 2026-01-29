from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.template import Template, TemplateCreate, TemplateUpdate
from app.services.template_service import TemplateService
from app.api.deps import get_db

router = APIRouter()

@router.post("/", response_model=Template)
def create_template(
    template_in: TemplateCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new template.
    """
    try:
        service = TemplateService(db)
        template = service.create_template(template_in)
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[Template])
def read_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve templates.
    """
    service = TemplateService(db)
    templates = service.get_templates(skip=skip, limit=limit)
    return templates

@router.get("/type/{document_type}", response_model=Template)
def read_template_by_type(
    document_type: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve a specific template by document type.
    """
    service = TemplateService(db)
    template = service.get_template_by_type(document_type)
    if not template:
        raise HTTPException(status_code=404, detail=f"No active template found for type: {document_type}")
    return template

@router.get("/{template_id}", response_model=Template)
def read_template(
    template_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve a specific template by ID.
    """
    service = TemplateService(db)
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=Template)
def update_template(
    template_id: int,
    template_in: TemplateUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Update an existing template.
    """
    service = TemplateService(db)
    try:
        template = service.update_template(template_id, template_in)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{template_id}", response_model=Template)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a template.
    """
    service = TemplateService(db)
    template = service.delete_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/{template_id}/clone", response_model=Template)
def clone_template(
    template_id: int,
    new_name: str,
    new_version: str = "1.0",
    db: Session = Depends(get_db)
) -> Any:
    """
    Clone an existing template.
    """
    service = TemplateService(db)
    cloned_template = service.clone_template(template_id, new_name, new_version)
    if not cloned_template:
        raise HTTPException(status_code=404, detail="Original template not found")
    return cloned_template

@router.post("/{template_id}/render")
def render_template(
    template_id: int,
    context: dict,
    db: Session = Depends(get_db)
) -> Any:
    """
    Render a template with provided context data.
    """
    service = TemplateService(db)
    rendered_content = service.render_template(template_id, context)
    if rendered_content is None:
        raise HTTPException(status_code=404, detail="Template not found or rendering failed")
    return {"rendered_content": rendered_content}
