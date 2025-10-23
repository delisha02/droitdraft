
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api import deps
from app.agents.document_generator.assembly_engine import assembly_engine

router = APIRouter()


@router.post("/generate", response_model=schemas.Document)
async def generate_document(
    *, 
    db: Session = Depends(deps.get_db),
    doc_in: schemas.DocumentGenerate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    Generate a new document.
    """
    template = crud.template.get(db, id=doc_in.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        generated_content = await assembly_engine.assemble_document(
            template=template.content,
            case_facts=doc_in.case_facts,
            title=doc_in.title
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc_create = schemas.DocumentCreate(title=doc_in.title, content=generated_content, owner_id=current_user.id)
    document = crud.document.create(db, obj_in=doc_create)
    return document
