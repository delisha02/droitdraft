from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.api import deps
from app.models.models import User
from app.services.export_service import export_service

router = APIRouter()

class ExportRequest(BaseModel):
    content: str
    title: str
    format: str # "pdf", "docx", "doc"
    font: Optional[str] = "Times New Roman"
    fontSize: Optional[str] = "12"
    lineHeight: Optional[str] = "1.5"

@router.post("/export")
async def export_document(
    *,
    request: ExportRequest,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Export document content to PDF or DOCX.
    """
    try:
        if request.format == "pdf":
            buffer = export_service.generate_pdf(
                request.content, 
                request.title, 
                font=request.font, 
                font_size=request.fontSize
            )
            media_type = "application/pdf"
            filename = f"{request.title}.pdf"
        elif request.format in ["docx", "doc"]:
            buffer = export_service.generate_docx(
                request.content, 
                request.title, 
                font=request.font, 
                font_size=request.fontSize
            )
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"{request.title}.docx"
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
