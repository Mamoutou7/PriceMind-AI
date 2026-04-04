from __future__ import annotations

from typing import Any

from apps.scraping_mcp.services.scrape_service import ScrapeService


def scrape_provider_tool(
    scrape_service: ScrapeService,
    provider_name: str,
    url: str,
    formats: list[str] | None = None,
) -> dict[str, Any]:
    return scrape_service.scrape_provider(
        provider_name=provider_name,
        url=url,
        formats=formats,
    )
