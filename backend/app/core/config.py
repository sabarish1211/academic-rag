from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GROQ_API_KEY: str
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "academic_docs"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    class Config:
        env_file = ".env"


settings = Settings()