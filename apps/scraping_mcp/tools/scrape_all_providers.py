from __future__ import annotations

from typing import Any

from apps.scraping_mcp.services.scrape_service import ScrapeService
from core.config import PROVIDER_URLS


def scrape_all_providers_tool(
    scrape_service: ScrapeService,
    formats: list[str] | None = None,
) -> dict[str, Any]:
    results: dict[str, Any] = {}

    for provider_name, url in PROVIDER_URLS.items():
        try:
            results[provider_name] = scrape_service.scrape_provider(
                provider_name=provider_name,
                url=url,
                formats=formats,
            )
        except Exception as exc:
            results[provider_name] = {
                "success": False,
                "error": str(exc),
            }

    return {
        "success": True,
        "data": results,
    }