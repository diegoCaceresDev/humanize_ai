from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Heading(BaseModel):
    level: str = Field(max_length=5)
    text: str = Field(max_length=500)


class ImageEvidence(BaseModel):
    src: str = Field(max_length=2_000)
    alt: str = Field(default="", max_length=500)
    width: int = Field(default=0, ge=0, le=20_000)
    height: int = Field(default=0, ge=0, le=20_000)


class FormEvidence(BaseModel):
    action: str = Field(default="", max_length=2_000)
    fields: list[str] = Field(default_factory=list, max_length=30)


class LinkEvidence(BaseModel):
    text: str = Field(max_length=500)
    href: str = Field(max_length=2_000)


class PageContext(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: HttpUrl
    title: str = Field(default="", max_length=1_000)
    description: str = Field(default="", max_length=3_000)
    language: str = Field(default="", max_length=20)
    headings: list[Heading] = Field(default_factory=list, max_length=100)
    calls_to_action: list[str] = Field(default_factory=list, max_length=120)
    forms: list[FormEvidence] = Field(default_factory=list, max_length=30)
    images: list[ImageEvidence] = Field(default_factory=list, max_length=100)
    links: list[LinkEvidence] = Field(default_factory=list, max_length=160)
    visible_text: str = Field(default="", max_length=50_000)
    html_snapshot: str = Field(default="", max_length=80_000)


class AuditRequest(BaseModel):
    context: PageContext
    screenshot: str = Field(min_length=20, max_length=10_000_000)

    @field_validator("screenshot")
    @classmethod
    def validate_screenshot(cls, value: str) -> str:
        if not value.startswith("data:image/"):
            raise ValueError("screenshot must be an image data URL")
        return value


class Finding(BaseModel):
    title: str = Field(max_length=200)
    severity: Literal["high", "medium", "low"]
    evidence: str = Field(max_length=1_000)
    recommendation: str = Field(max_length=2_000)


class ResearchSource(BaseModel):
    title: str = Field(max_length=300)
    url: str = Field(max_length=2_000)


class AuditResult(BaseModel):
    score: int = Field(ge=0, le=100)
    score_label: str = Field(max_length=100)
    summary: str = Field(max_length=3_000)
    findings: list[Finding] = Field(min_length=1, max_length=12)
    quick_wins: list[str] = Field(min_length=1, max_length=12)
    research_sources: list[ResearchSource] = Field(default_factory=list, max_length=10)


class AuditResponse(AuditResult):
    id: str
    url: str
    created_at: datetime

