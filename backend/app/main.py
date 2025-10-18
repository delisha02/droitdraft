from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.services.storage import get_storage
from app.core.config import settings

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    storage_client = get_storage()
    bucket_name = settings.MINIO_BUCKET
    if not storage_client.bucket_exists(bucket_name):
        storage_client.make_bucket(bucket_name)

@app.get("/")
def read_root():
    return {"message": "Welcome to DroitDraft"}