import asyncio

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app import main
from app.providers import _clean_json, humanize_page
from app.schemas import AuditRequest, PageContext


def test_screenshot_must_be_an_image_data_url() -> None:
    with pytest.raises(ValidationError):
        AuditRequest.model_validate({"context": {"url": "https://example.com"}, "screenshot": "not-an-image"})


def test_clean_json_accepts_markdown_fences() -> None:
    assert _clean_json('```json\n{"score": 42}\n```') == {"score": 42}


def test_demo_mode_produces_a_valid_audit() -> None:
    page = PageContext.model_validate({"url": "https://example.com", "title": "Example", "headings": [{"level": "h1", "text": "A useful headline"}]})
    result = asyncio.run(humanize_page(page, "data:image/jpeg;base64,abc", Settings(demo_mode=True)))
    assert result.score == 68
    assert result.findings[0].evidence == "A useful headline"


def test_settings_accept_existing_local_key_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPEN_ROUTER", "openrouter-test-key")
    monkeypatch.setenv("EXA_AI", "exa-test-key")
    settings = Settings(_env_file=None)
    assert settings.openrouter_api_key == "openrouter-test-key"
    assert settings.exa_api_key == "exa-test-key"


def test_settings_accept_neon_database_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NEON_DATABASE_URL", "postgresql://neon.example/db")
    monkeypatch.setenv("DATABASE_URL_UNPOOLED", "postgresql://direct.neon.example/db?sslmode=require&channel_binding=require")
    settings = Settings(_env_file=None)
    assert settings.database_url == "postgresql://neon.example/db"
    assert settings.async_database_url == "postgresql+asyncpg://neon.example/db"
    assert settings.async_database_url_unpooled == "postgresql+asyncpg://direct.neon.example/db?ssl=require"


def test_settings_normalize_neon_ssl_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://neon.example/db?sslmode=require&channel_binding=require")
    settings = Settings()
    assert settings.async_database_url == "postgresql+asyncpg://neon.example/db?ssl=require"


def test_history_endpoint_explains_missing_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "engine", None)
    monkeypatch.setattr(main, "session_factory", None)
    response = TestClient(main.app).get("/api/audits/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 503


def test_audit_payload_is_rejected_before_parsing_when_oversized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "engine", None)
    monkeypatch.setattr(main.settings, "max_request_bytes", 10)
    response = TestClient(main.app).post("/api/audits", content=b"01234567890", headers={"content-type": "application/json"})
    assert response.status_code == 413


def test_readiness_explains_missing_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "engine", None)
    response = TestClient(main.app).get("/readyz")
    assert response.status_code == 503
