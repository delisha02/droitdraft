
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.models.models import User # Import User explicitly
from app.schemas import document as schemas_document
from app.schemas.document import DocumentGenerate, GhostSuggestRequest, GhostSuggestResponse
from app.api import deps
from app.agents.document_generator.assembly_engine import assembly_engine
from app.agents.document_generator.ghost_typing import ghost_typing_engine
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

    # 2. Process file_ids if present in case_facts
    file_ids = doc_in.case_facts.get("file_ids", [])
    merged_facts = doc_in.case_facts.copy()
    
    # Inject current date for automatic placeholder filling
    from datetime import datetime
    today_str = datetime.now().strftime("%B %d, %Y")
    merged_facts["today's_date"] = today_str
    merged_facts["drafting_date"] = today_str
    merged_facts["current_date"] = today_str
    
    if file_ids:
        from app.agents.document_processor.text_extractor import TextExtractor
        from app.agents.document_processor.llm_extractor import llm_extractor
        from app.services import storage
        
        extractor = TextExtractor()
        all_extracted_text = ""
        
        for fid in file_ids:
            local_path = None
            try:
                local_path = storage.download_file(fid)
                text = extractor.extract_text(local_path)
                if text:
                   all_extracted_text += f"\n--- Evidence from {fid} ---\n{text}\n"
            except Exception as e:
                print(f"Failed to process file {fid}: {e}")
            finally:
                if local_path:
                    storage.delete_local_file(local_path)
        
        if all_extracted_text:
            # Add raw evidence to facts for the assembly engine to use
            merged_facts["evidence_text"] = all_extracted_text
            # Use LLM to structure facts from the collected evidence
            evidence_facts = await llm_extractor.extract(all_extracted_text)
            # Merge evidence facts into merged_facts (prompt takes precedence if keys conflict)
            for k, v in evidence_facts.items():
                if k not in merged_facts or not merged_facts[k]:
                    merged_facts[k] = v

    try:
        generated_content = await assembly_engine.assemble_document(
            template=template.content,
            case_facts=merged_facts,
            title=doc_in.title
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create a simple DocumentCreate (title and content)
    doc_create = schemas_document.DocumentCreate(title=doc_in.title, content=generated_content)
    # Save with owner_id using the specialized method
    document = crud.document.create_with_owner(db, obj_in=doc_create, owner_id=current_user.id)
    return document


@router.post("/ghost-suggest", response_model=GhostSuggestResponse)
async def ghost_suggest(
    *,
    request: GhostSuggestRequest,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Predict the next sentence for the document.
    """
    suggestion = await ghost_typing_engine.suggest_next_sentence(
        current_content=request.current_content,
        case_facts=request.case_facts,
        doc_type=request.doc_type
    )
    return GhostSuggestResponse(suggestion=suggestion)


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
