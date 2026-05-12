from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    DATABASE_URL: str = "sqlite:///../dataset/dev.db"
    SECRET_KEY: str = "super-secret-key-for-mvp"
    GEMINI_API_KEY: str = ""
    JWT_EXPIRE_MINUTES: int = 1440
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()
