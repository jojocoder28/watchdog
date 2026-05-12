from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-for-mvp-1234"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    GEMINI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
