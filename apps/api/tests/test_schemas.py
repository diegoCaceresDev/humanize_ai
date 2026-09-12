import asyncio

import pytest
from pydantic import ValidationError

from app.config import Settings
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
    settings = Settings()
    assert settings.openrouter_api_key == "openrouter-test-key"
    assert settings.exa_api_key == "exa-test-key"
