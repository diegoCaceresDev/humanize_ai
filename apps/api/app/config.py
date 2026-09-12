from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    demo_mode: bool = False
    database_url: str = Field(default="", validation_alias=AliasChoices("DATABASE_URL", "NEON_DATABASE_URL", "NEON_URL"))
    database_url_unpooled: str = Field(default="", validation_alias=AliasChoices("DATABASE_URL_UNPOOLED", "NEON_DATABASE_URL_UNPOOLED"))
    openrouter_api_key: str = Field(default="", validation_alias=AliasChoices("OPENROUTER_API_KEY", "OPEN_ROUTER"))
    openrouter_model: str = "google/gemini-2.5-flash"
    exa_api_key: str = Field(default="", validation_alias=AliasChoices("EXA_API_KEY", "EXA_AI"))
    exa_enabled: bool = False
    allowed_origins: str = "http://localhost:3000"
    allow_any_chrome_extension_origin: bool = True
    max_request_bytes: int = 12_000_000

    model_config = SettingsConfigDict(
        env_file=(Path(__file__).resolve().parents[3] / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def chrome_extension_origin_regex(self) -> str | None:
        return r"chrome-extension://.*" if self.allow_any_chrome_extension_origin else None

    @property
    def async_database_url(self) -> str:
        return self._asyncpg_url(self.database_url)

    @property
    def async_database_url_unpooled(self) -> str:
        return self._asyncpg_url(self.database_url_unpooled)

    @staticmethod
    def _asyncpg_url(value: str) -> str:
        if not value:
            return value
        normalized_value = value.strip().strip("\\\"'")
        parsed = urlsplit(normalized_value.replace("postgres://", "postgresql://", 1))
        query = {key: item.strip("\\\"'") for key, item in parse_qsl(parsed.query, keep_blank_values=True)}
        if "sslmode" in query and "ssl" not in query:
            query["ssl"] = query["sslmode"]
        query.pop("sslmode", None)
        query.pop("channel_binding", None)
        normalized = urlunsplit(parsed._replace(query=urlencode(query)))
        return normalized.replace("postgresql://", "postgresql+asyncpg://", 1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
