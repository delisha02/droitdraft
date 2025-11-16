
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.models.models import User # Import User explicitly
from app.schemas import document as schemas_document
from app.schemas.document import DocumentGenerate
from app.api import deps
from app.agents.document_generator.assembly_engine import assembly_engine
from app.integrations.indiankanoon.data_processor import IndianKanoonDataProcessor

router = APIRouter()


@router.post("/generate", response_model=schemas_document.Document)
async def generate_document(
    *,
    db: Session = Depends(deps.get_db),
    doc_in: DocumentGenerate,
    current_user: User = Depends(deps.get_current_active_user)
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

    doc_create = schemas_document.DocumentCreate(title=doc_in.title, content=generated_content, owner_id=current_user.id)
    document = crud.document.create(db, obj_in=doc_create)
    return document


@router.post("/indiankanoon/process/{doc_id}", response_model=dict)
async def process_indian_kanoon_document(
    *,
    db: Session = Depends(deps.get_db),
    doc_id: str,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Fetch, process, and store a document from Indian Kanoon.
    """
    processor = IndianKanoonDataProcessor(db)
    try:
        await processor.process_document(doc_id)
        return {"message": f"Document {doc_id} processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await processor.close()
