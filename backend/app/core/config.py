from pydantic_settings import BaseSettings

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

    CHROMA_HOST: str
    CHROMA_PORT: int

    GROQ_API_KEY: str
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

settings = Settings()

HYBRID_SEARCH_CONFIG = {
    "fusion_algorithm": "reciprocal_rank_fusion",
    "keyword_alpha": 0.7, # Weight for BM25 in keyword-heavy queries
    "semantic_alpha": 0.3, # Weight for BM25 in semantic queries
    "k": 60, # For RRF
    "boost_factors": {
        "jurisdiction": "US",
        "jurisdiction_boost": 1.5,
        "recency_days": 365,
        "recency_boost": 1.2
    }
}

