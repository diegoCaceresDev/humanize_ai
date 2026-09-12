import asyncio
import json

import httpx
import pytest

from app.config import Settings
from app.providers import humanize_page
from app.schemas import PageContext


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeAsyncClient:
    requests: list[dict] = []
    exa_fails = False

    def __init__(self, **_: object):
        pass

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.requests.append({"url": url, **kwargs})
        if "exa.ai" in url:
            if self.exa_fails:
                raise httpx.ConnectError("Exa unavailable")
            return FakeResponse({"results": [{"title": "UX reference", "url": "https://reference.example/ux"}]})
        result = {
            "score": 81,
            "score_label": "Clear and confident",
            "summary": "The page makes a clear promise.",
            "findings": [{"title": "CTA hierarchy", "severity": "low", "evidence": "Get started", "recommendation": "Keep one primary CTA."}],
            "quick_wins": ["Clarify the supporting proof."],
            "research_sources": [],
        }
        return FakeResponse({"choices": [{"message": {"content": json.dumps(result)}}]})


def page() -> PageContext:
    return PageContext.model_validate({
        "url": "https://example.com",
        "title": "Example product",
        "headings": [{"level": "h1", "text": "A useful headline"}],
        "calls_to_action": ["Get started"],
    })


def test_openrouter_request_contains_page_evidence_and_screenshot(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeAsyncClient.requests = []
    FakeAsyncClient.exa_fails = False
    monkeypatch.setattr("app.providers.httpx.AsyncClient", FakeAsyncClient)
    result = asyncio.run(humanize_page(page(), "data:image/jpeg;base64,abc", Settings(openrouter_api_key="test", _env_file=None)))

    request = next(item for item in FakeAsyncClient.requests if "openrouter.ai" in item["url"])
    messages = request["json"]["messages"]
    assert result.score == 81
    assert messages[0]["role"] == "system"
    assert "untrusted data" in messages[0]["content"]
    assert messages[1]["content"][1]["image_url"]["url"].startswith("data:image/jpeg")
    assert request["json"]["response_format"] == {"type": "json_object"}


def test_exa_sources_are_returned_as_grounding_context(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeAsyncClient.requests = []
    FakeAsyncClient.exa_fails = False
    monkeypatch.setattr("app.providers.httpx.AsyncClient", FakeAsyncClient)
    settings = Settings(openrouter_api_key="test", exa_api_key="test", exa_enabled=True, _env_file=None)
    result = asyncio.run(humanize_page(page(), "data:image/jpeg;base64,abc", settings))

    assert result.research_sources[0].url == "https://reference.example/ux"
    exa_request = next(item for item in FakeAsyncClient.requests if "exa.ai" in item["url"])
    assert exa_request["json"]["type"] in {"auto", "fast"}
    assert "highlights" in exa_request["json"]["contents"]


def test_exa_failure_does_not_block_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeAsyncClient.requests = []
    FakeAsyncClient.exa_fails = True
    monkeypatch.setattr("app.providers.httpx.AsyncClient", FakeAsyncClient)
    settings = Settings(openrouter_api_key="test", exa_api_key="test", exa_enabled=True, _env_file=None)
    result = asyncio.run(humanize_page(page(), "data:image/jpeg;base64,abc", settings))

    assert result.score == 81
    assert result.research_sources == []
    assert any("openrouter.ai" in item["url"] for item in FakeAsyncClient.requests)
