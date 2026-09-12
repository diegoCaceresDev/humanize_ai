import asyncio

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app import main
from app.providers import _clean_json, humanize_page
from app.schemas import AuditRequest, AuditResult, Finding, PageContext


def test_screenshot_must_be_an_image_data_url() -> None:
    with pytest.raises(ValidationError):
        AuditRequest.model_validate({"context": {"url": "https://example.com"}, "screenshot": "not-an-image"})


def test_audit_request_accepts_bounded_browser_evidence() -> None:
    request = AuditRequest.model_validate({
        "context": {"url": "https://example.com"},
        "screenshot": "data:image/jpeg;base64,abc",
        "browser_evidence": {
            "elements": [{"id": "cta-1", "role": "primary-cta", "label": "Book a demo", "bounds": {"x": 10, "y": 20, "width": 120, "height": 40}, "viewportVisible": True, "prominence": 72}],
            "metrics": {"visibleCtaCount": 3, "heroCtaCount": 2, "missingAltCount": 1, "unlabeledFormFieldCount": 0, "primaryActionProminence": 72, "primaryCtaLabel": "Book a demo", "method": "browser-structural-v1"},
        },
    })
    assert request.browser_evidence is not None
    assert request.browser_evidence.elements[0].label == "Book a demo"


def test_browser_evidence_rejects_unbounded_prominence() -> None:
    with pytest.raises(ValidationError):
        AuditRequest.model_validate({
            "context": {"url": "https://example.com"},
            "screenshot": "data:image/jpeg;base64,abc",
            "browser_evidence": {"elements": [], "metrics": {"visibleCtaCount": 0, "heroCtaCount": 0, "missingAltCount": 0, "unlabeledFormFieldCount": 0, "primaryActionProminence": 101, "primaryCtaLabel": "", "method": "browser-structural-v1"}},
        })


def test_audit_endpoint_forwards_bounded_browser_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    async def audit_stub(*_args, **_kwargs) -> AuditResult:
        return AuditResult(score=80, score_label="Measured", summary="A measured response.", findings=[Finding(title="CTA competition", severity="medium", evidence="Observed 3 CTAs", recommendation="Choose one primary action.")], quick_wins=["Keep the preview reversible."])

    monkeypatch.setattr(main, "engine", None)
    monkeypatch.setattr(main, "session_factory", None)
    monkeypatch.setattr(main, "humanize_page", audit_stub)
    response = TestClient(main.app).post("/api/audits", json={
        "context": {"url": "https://example.com"},
        "screenshot": "data:image/jpeg;base64,abc",
        "browser_evidence": {
            "elements": [{"id": "cta-1", "role": "primary-cta", "label": "Book a demo", "bounds": {"x": 10, "y": 20, "width": 120, "height": 40}, "viewportVisible": True, "prominence": 72}],
            "metrics": {"visibleCtaCount": 3, "heroCtaCount": 2, "missingAltCount": 1, "unlabeledFormFieldCount": 0, "primaryActionProminence": 72, "primaryCtaLabel": "Book a demo", "method": "browser-structural-v1"},
        },
    })
    assert response.status_code == 200
    assert response.json()["score"] == 80


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


def test_settings_can_disable_broad_chrome_extension_cors() -> None:
    settings = Settings(allowed_origins="chrome-extension://abcdefghijklmnop", allow_any_chrome_extension_origin=False, _env_file=None)
    assert settings.origins == ["chrome-extension://abcdefghijklmnop"]
    assert settings.chrome_extension_origin_regex is None


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
