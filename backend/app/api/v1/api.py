'''
This file combines all the routers.
'''

from fastapi import APIRouter

from app.api.v1.endpoints import auth, templates

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
