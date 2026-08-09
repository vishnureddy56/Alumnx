import os
from pydantic_settings import BaseSettings
from typing import Optional


def normalize_candidate_id(candidate_id: Optional[str]) -> str:
    if not candidate_id:
        return "[EMAIL_ADDRESS]"
    return candidate_id.strip().lower()


class Settings(BaseSettings):
    CANDIDATE_ID: str = "[EMAIL_ADDRESS]"
    DATABASE_URL: str = "sqlite:///./routeiq.db"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    FRONTEND_URL: str = "http://localhost:5173"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def normalized_candidate_id(self) -> str:
        return normalize_candidate_id(self.CANDIDATE_ID)


settings = Settings()
