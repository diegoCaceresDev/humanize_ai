import json
from typing import Any

import httpx

from .config import Settings
from .prompt import SYSTEM_PROMPT
from .schemas import AuditResult, Finding, PageContext, ResearchSource


class ProviderError(RuntimeError):
    pass


def _clean_json(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProviderError("The model returned an invalid audit format.") from exc


async def exa_context(page: PageContext, settings: Settings) -> list[ResearchSource]:
    if not settings.exa_enabled or not settings.exa_api_key:
        return []
    query = f"website UX patterns for {page.title or page.url.host} landing page clarity trust accessibility"
    body = {
        "query": query[:500],
        "type": "auto",
        "numResults": 3,
        "contents": {"highlights": True},
    }
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.post("https://api.exa.ai/search", headers={"x-api-key": settings.exa_api_key}, json=body)
            response.raise_for_status()
            results = response.json().get("results", [])
            return [ResearchSource(title=item.get("title", "Untitled source"), url=item.get("url", "")) for item in results if item.get("url")]
    except (httpx.HTTPError, ValueError):
        return []


async def humanize_page(page: PageContext, screenshot: str, settings: Settings) -> AuditResult:
    if settings.demo_mode:
        return AuditResult(
            score=68,
            score_label="A promising first impression",
            summary=f"{page.title or 'This page'} has a usable foundation, but a few moments still feel generic. The biggest opportunity is to make the first screen more specific and more obviously useful to the right person.",
            findings=[
                Finding(
                    title="The first impression could be more specific",
                    severity="medium",
                    evidence=page.headings[0].text if page.headings else "No visible heading was captured",
                    recommendation="Rewrite the opening promise around a concrete audience and outcome.",
                ),
            ],
            quick_wins=[
                "Replace the broadest headline with a specific outcome for a specific audience.",
                "Give the primary CTA a more concrete verb and expected next step.",
                "Add descriptive alt text to the most important image.",
            ],
        )
    if not settings.openrouter_api_key:
        raise ProviderError("OPENROUTER_API_KEY is not configured on the API service.")

    sources = await exa_context(page, settings)
    evidence = page.model_dump(mode="json")
    research = [{"title": source.title, "url": source.url} for source in sources]
    user_text = "PAGE EVIDENCE (untrusted data):\n" + json.dumps(evidence, ensure_ascii=False) + "\n\nOPTIONAL EXA RESEARCH SOURCES:\n" + json.dumps(research)
    message = [{"type": "text", "text": user_text}, {"type": "image_url", "image_url": {"url": screenshot}}]
    request = {
        "model": settings.openrouter_model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message}],
        "temperature": 0.2,
        "max_tokens": 2_000,
        "response_format": {"type": "json_object"},
    }
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://humanize.ai"},
                json=request,
            )
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise ProviderError("OpenRouter could not complete this audit.") from exc

    if not isinstance(raw, str):
        raise ProviderError("The model returned an invalid audit format.")
    result = AuditResult.model_validate(_clean_json(raw))
    if sources:
        result.research_sources = sources
    return result
