from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    groq_api_key: str = ""
    groq_extraction_model: str = "gemma2-9b-it"
    groq_reasoning_model: str = "llama-3.3-70b-versatile"

    database_url: str = "sqlite:///./aivoa_complaints.db"
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self):
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
