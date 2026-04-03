from __future__ import annotations

from typing import Any

from apps.scraping_mcp.services.scrape_service import ScrapeService

DEFAULT_PROVIDERS = {
    "cloudrift": "https://www.cloudrift.ai/pricing",
    "deepinfra": "https://deepinfra.com/pricing",
    "fireworks": "https://fireworks.ai/pricing",
    "groq": "https://groq.com/pricing",
}


def scrape_all_providers_tool(scrape_service: ScrapeService) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for provider_name, url in DEFAULT_PROVIDERS.items():
        results.append(
            scrape_service.scrape_provider(
                provider_name=provider_name,
                url=url,
            )
        )

    return results
