import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Authentication
    api_token: str = ""
    
    # Server settings
    port: int = 8000
    log_level: str = "INFO"
    
    # Presidio settings
    default_language: str = "en"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
