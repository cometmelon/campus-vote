"""Application configuration using pydantic-settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./campusvote.db"
    
    # JWT
    SECRET_KEY: str = "campusvote-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Email (Resend)
    RESEND_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@campusvote.edu"
    
    # Voting Queue
    VOTING_LINK_EXPIRE_HOURS: int = 24
    DEFAULT_BATCH_SIZE: int = 60
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
