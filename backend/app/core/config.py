from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import field_validator
import os

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str

    @field_validator("MINIO_ENDPOINT", "MINIO_ACCESS_KEY", "MINIO_SECRET_KEY")
    @classmethod
    def strip_minio_whitespace(cls, v: str) -> str:
        return v.strip()

    CHROMA_HOST: str
    CHROMA_PORT: int

    GROQ_API_KEY: Optional[str] = None
    GROQ_API_KEY_2: Optional[str] = None
    GROQ_API_KEY_3: Optional[str] = None
    GROQ_API_KEY_4: Optional[str] = None
    GROQ_API_KEY_5: Optional[str] = None
    GROQ_API_KEY_PROJECT: Optional[str] = None
    GEMINI_API_KEY: str
    INDIAN_KANOON_API_KEY: str
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    UPLOAD_DIR: str
    PROCESSED_DIR: str

    # CORS
    CORS_ORIGINS: str

    # JWT settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

HYBRID_SEARCH_CONFIG = {
    "fusion_algorithm": "reciprocal_rank_fusion",
    "keyword_weight": 0.6,  # Sparse/BM25 retriever weight
    "semantic_weight": 0.4,  # Dense vector retriever weight
    "rrf_k": 60,  # RRF constant
    "top_k": 5,  # default retrieval depth
    "boost_factors": {
        "jurisdiction": "India",
        "jurisdiction_boost": 1.5,
        "recency_days": 365,
        "recency_boost": 1.2
    }
}
