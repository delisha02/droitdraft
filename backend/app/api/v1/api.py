'''
This file combines all the routers.
'''

from fastapi import APIRouter

from app.api.v1.endpoints import auth, templates, documents, livelaw, corpus, orchestrator

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(livelaw.router, prefix="/livelaw", tags=["livelaw"])
api_router.include_router(corpus.router, prefix="/corpus", tags=["corpus"])
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["orchestrator"])
