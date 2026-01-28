from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Any
import traceback
from app.api import deps
from app.services import storage

router = APIRouter()

@router.post("/", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a document for processing/fact extraction.
    """
    if not file.content_type in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload a PDF or an image (JPG/PNG)."
        )
    
    try:
        content = await file.read()
        filename = storage.upload_file(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type
        )
        return {
            "message": "File uploaded successfully",
            "filename": filename,
            "original_name": file.filename
        }
    except Exception as e:
        print(f"Upload failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/extract/{filename}", status_code=200)
async def extract_facts(
    filename: str,
    current_user: Any = Depends(deps.get_current_active_user),
) -> Any:
    """
    Extract structured facts from an uploaded document using LLM.
    """
    # Import inside to avoid circular imports or startup issues
    from app.agents.document_processor.text_extractor import TextExtractor
    from app.agents.document_processor.llm_extractor import llm_extractor
    
    local_path = None
    try:
        print(f"Starting extraction for: {filename}")
        
        # 1. Download from MinIO
        try:
            local_path = storage.download_file(filename)
        except Exception as e:
            print(f"MinIO download failed: {e}")
            raise HTTPException(status_code=404, detail=f"File not found in storage: {filename}")
        
        # 2. Extract raw text
        extractor = TextExtractor()
        raw_text = extractor.extract_text(local_path)
        
        if not raw_text or not raw_text.strip():
            print("No text extracted from document.")
            raise HTTPException(status_code=400, detail="No text could be extracted from the document.")
        
        print(f"Extracted {len(raw_text)} characters from document.")
        
        # 3. Use LLM to structure facts
        facts = await llm_extractor.extract(raw_text)
        
        return {
            "filename": filename,
            "facts": facts,
            "raw_text_preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Extraction API failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        # 4. Cleanup
        if local_path:
            storage.delete_local_file(local_path)
