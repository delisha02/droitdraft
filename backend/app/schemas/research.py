from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ResearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 5

class ResearchSource(BaseModel):
    title: Optional[str]
    url: Optional[str]
    source: Optional[str]
    id: Optional[str]

class ResearchResponse(BaseModel):
    answer: str
    sources: List[ResearchSource]
