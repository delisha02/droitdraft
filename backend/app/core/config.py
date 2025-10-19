from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    CHROMA_HOST: str
    CHROMA_PORT: int

    GROQ_API_KEY: str
    GEMINI_API_KEY: str

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
