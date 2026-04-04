from __future__ import annotations

from typing import Any

from apps.scraping_mcp.services.metadata_service import MetadataService


def get_scrape_result_tool(
    metadata_service: MetadataService,
    provider_name: str,
) -> dict[str, Any]:
    metadata = metadata_service.load()
    normalized_provider = provider_name.strip().lower()

    provider_metadata = metadata.get(normalized_provider)
    if not provider_metadata:
        return {
            "success": False,
            "error": f"No metadata found for provider '{normalized_provider}'.",
        }

    return {
        "success": True,
        "data": provider_metadata,
    }
