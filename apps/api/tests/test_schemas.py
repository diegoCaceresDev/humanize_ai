import pytest
from pydantic import ValidationError

from app.schemas import AuditRequest


def test_screenshot_must_be_an_image_data_url() -> None:
    with pytest.raises(ValidationError):
        AuditRequest.model_validate({"context": {"url": "https://example.com"}, "screenshot": "not-an-image"})

