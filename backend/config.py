"""Configuration settings"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://challenge:challenge_2024@localhost:5432/challenge_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"


settings = Settings()
