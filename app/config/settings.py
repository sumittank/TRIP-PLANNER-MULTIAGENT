"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Travel Planning System"
    app_version: str = "2.0.0"
    debug: bool = False

    groq_api_key: str = ""
    tavily_api_key: str = ""
    aviationstack_api_key: str = ""
    database_url: str = "postgresql+psycopg://postgres:root@localhost:5432/langgraph_memory_db"

    groq_model: str = "llama-3.3-70b-versatile"
    max_retries: int = 3
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    cache_ttl_seconds: int = 300

    cors_origins: list[str] = ["*"]
    travel_plans_dir: str = "travel_plans"


@lru_cache
def get_settings() -> Settings:
    return Settings()
