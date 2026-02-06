from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.research import ResearchQuery, ResearchResponse
from app.agents.legal_research.agent import LegalResearchAgent
from app.models.models import User

router = APIRouter()
research_agent = LegalResearchAgent()

@router.post("/query", response_model=ResearchResponse)
async def research_query(
    *,
    db: Session = Depends(deps.get_db),
    query_in: ResearchQuery,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Perform legal research using the RAG agent.
    """
    try:
        result = await research_agent.answer_query(query_in.query, k=query_in.limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
