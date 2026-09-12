from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    demo_mode: bool = False
    database_url: str = ""
    openrouter_api_key: str = Field(default="", validation_alias=AliasChoices("OPENROUTER_API_KEY", "OPEN_ROUTER"))
    openrouter_model: str = "google/gemini-2.5-flash"
    exa_api_key: str = Field(default="", validation_alias=AliasChoices("EXA_API_KEY", "EXA_AI"))
    exa_enabled: bool = False
    allowed_origins: str = "http://localhost:3000"
    max_request_bytes: int = 12_000_000

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parents[3] / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
