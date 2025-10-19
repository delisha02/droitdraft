from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.db.database import engine, Base
# from app.services.storage import get_storage
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DroitDraft API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# def startup_event():
#     storage_client = get_storage()
#     bucket_name = settings.MINIO_BUCKET
#     if not storage_client.bucket_exists(bucket_name):
#         storage_client.make_bucket(bucket_name)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to DroitDraft"}