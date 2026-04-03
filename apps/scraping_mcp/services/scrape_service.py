from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from apps.scraping_mcp.services.firecrawl_service import FirecrawlService
from apps.scraping_mcp.services.metadata_service import MetadataService
from apps.scraping_mcp.services.raw_document_service import RawDocumentService

ALLOWED_PROVIDERS = {
    "cloudrift",
    "deepinfra",
    "fireworks",
    "groq",
}


class ScrapeService:
    """Coordinates scraping, raw file persistence and metadata persistence."""

    def __init__(
        self,
        firecrawl_service: FirecrawlService,
        raw_document_service: RawDocumentService,
        metadata_service: MetadataService,
    ) -> None:
        self._firecrawl_service = firecrawl_service
        self._raw_document_service = raw_document_service
        self._metadata_service = metadata_service

    def scrape_provider(
        self,
        provider_name: str,
        url: str,
        formats: list[str] | None = None,
    ) -> dict[str, Any]:
        self._validate_provider(provider_name)

        resolved_formats = formats or ["markdown", "html"]
        result = self._firecrawl_service.scrape(url=url, formats=resolved_formats)

        metadata = self._metadata_service.load()
        provider_metadata: dict[str, Any] = {
            "provider_name": provider_name,
            "url": url,
            "domain": urlparse(url).netloc,
            "scraped_at": datetime.now(UTC).isoformat(),
            "formats": resolved_formats,
            "success": False,
            "content_files": {},
            "title": "",
            "description": "",
        }

        if bool(result.get("success", True)):
            for format_name in resolved_formats:
                content = result.get(format_name)
                if not content:
                    continue

                file_path = self._raw_document_service.save(
                    provider_name,
                    format_name,
                    content,
                )
                content_files = provider_metadata["content_files"]
                if not isinstance(content_files, dict):
                    raise TypeError("content_files must be a dictionary.")
                content_files[format_name] = file_path

            raw_metadata = result.get("metadata", {})
            metadata_block = raw_metadata if isinstance(raw_metadata, dict) else {}

            provider_metadata["title"] = str(metadata_block.get("title", ""))
            provider_metadata["description"] = str(
                metadata_block.get("description", "")
            )
            provider_metadata["success"] = True

        metadata[provider_name] = provider_metadata
        self._metadata_service.save(metadata)

        return provider_metadata

    @staticmethod
    def _validate_provider(provider_name: str) -> None:
        if provider_name.lower() not in ALLOWED_PROVIDERS:
            raise ValueError(f"Provider '{provider_name}' is not allowed.")
