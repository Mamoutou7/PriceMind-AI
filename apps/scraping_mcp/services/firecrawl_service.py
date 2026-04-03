from __future__ import annotations

import os
from typing import Any, cast
from dotenv import load_dotenv

from firecrawl import FirecrawlApp

load_dotenv()

class FirecrawlService:
    """Small wrapper around Firecrawl SDK."""

    def __init__(self, api_key: str | None = None) -> None:
        resolved_api_key = api_key or os.getenv("FIRECRAWL_API_KEY", "").strip()
        if not resolved_api_key:
            raise ValueError("FIRECRAWL_API_KEY is required.")
        self._client = FirecrawlApp(api_key=resolved_api_key)

    def scrape(self, url: str, formats: list[str]) -> dict[str, Any]:
        result: Any = self._client.scrape(url, formats=formats)

        if hasattr(result, "model_dump"):
            dumped = result.model_dump()
            if not isinstance(dumped, dict):
                raise TypeError("Unexpected Firecrawl dumped response type.")
            return cast(dict[str, Any], dumped)

        if isinstance(result, dict):
            return cast(dict[str, Any], result)

        raise TypeError("Unexpected Firecrawl response type.")
