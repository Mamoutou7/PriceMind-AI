from __future__ import annotations

from typing import Any, cast

from firecrawl import FirecrawlApp

from core.settings import get_settings


class FirecrawlService:
    """Small wrapper around the Firecrawl SDK."""

    def __init__(self, client: FirecrawlApp | None = None) -> None:
        self._client = client

    def scrape(self, url: str, formats: list[str]) -> dict[str, Any]:
        settings = get_settings()
        api_key = settings.firecrawl_api_key

        if not api_key and self._client is None:
            raise ValueError("FIRECRAWL_API_KEY is required.")

        if self._client is None:
            self._client = FirecrawlApp(api_key=api_key)

        result: Any = self._client.scrape(url, formats=formats)

        if hasattr(result, "model_dump"):
            dumped = result.model_dump()
            if not isinstance(dumped, dict):
                raise TypeError("Unexpected Firecrawl dumped response type.")
            return cast(dict[str, Any], dumped)

        if isinstance(result, dict):
            return cast(dict[str, Any], result)

        raise TypeError("Unexpected Firecrawl response type.")
