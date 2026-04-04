from __future__ import annotations

import pytest

from apps.scraping_mcp.services.scrape_service import ScrapeService

pytestmark = pytest.mark.unit


class DummyFirecrawlService:
    def scrape(self, url: str, formats: list[str]) -> dict:
        return {
            "success": True,
            "markdown": "# Pricing\n\nSome markdown content",
            "html": "<html><body>Pricing</body></html>",
            "metadata": {
                "title": "Groq Pricing",
                "description": "Groq pricing page",
            },
        }


class DummyRawDocumentService:
    def __init__(self) -> None:
        self.saved: list[tuple[str, str, str]] = []

    def save(self, provider_name: str, format_name: str, content: str) -> str:
        self.saved.append((provider_name, format_name, content))
        return f"/tmp/{provider_name}/page.{format_name}.txt"


class DummyMetadataService:
    def __init__(self) -> None:
        self.data: dict = {}
        self.saved_payload: dict | None = None

    def load(self) -> dict:
        return dict(self.data)

    def save(self, metadata: dict) -> None:
        self.saved_payload = metadata
        self.data = dict(metadata)


def test_scrape_service_success() -> None:
    firecrawl = DummyFirecrawlService()
    raw_doc = DummyRawDocumentService()
    metadata = DummyMetadataService()

    service = ScrapeService(
        firecrawl_service=firecrawl,
        raw_document_service=raw_doc,
        metadata_service=metadata,
    )

    result = service.scrape_provider(
        provider_name="groq",
        url="https://groq.com/pricing",
    )

    assert result["success"] is True
    assert result["provider_name"] == "groq"
    assert result["title"] == "Groq Pricing"
    assert result["description"] == "Groq pricing page"
    assert "markdown" in result
    assert "html" in result

    assert len(raw_doc.saved) == 2
    assert metadata.saved_payload is not None
    assert "groq" in metadata.saved_payload


def test_scrape_service_rejects_unknown_provider() -> None:
    firecrawl = DummyFirecrawlService()
    raw_doc = DummyRawDocumentService()
    metadata = DummyMetadataService()

    service = ScrapeService(
        firecrawl_service=firecrawl,
        raw_document_service=raw_doc,
        metadata_service=metadata,
    )

    with pytest.raises(ValueError, match="not allowed"):
        service.scrape_provider(
            provider_name="unknown-provider",
            url="https://example.com/pricing",
        )
