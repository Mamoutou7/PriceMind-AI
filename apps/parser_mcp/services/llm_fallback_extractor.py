from __future__ import annotations

import json
import os
from typing import Any, cast

from anthropic import Anthropic

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")


class LLMFallbackExtractor:
    """Uses an LLM only when deterministic extraction is insufficient."""

    def __init__(self, client: Anthropic = None) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self._client = client or Anthropic(api_key=api_key)

    def extract(self, provider_name: str, raw_content: str) -> list[dict[str, Any]]:
        prompt = f"""
Extract pricing data from the following provider page.

Rules:
- Return only valid JSON.
- Return a JSON array.
- Each item must contain:
  provider_name, model_name, input_price_per_1m, output_price_per_1m, currency
- Use null when a price is missing.

Provider: {provider_name}

Content:
{raw_content[:12000]}
"""

        response = self._client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        text_parts: list[str] = []
        for block in response.content:
            block_type = getattr(block, "type", None)
            if block_type != "text":
                continue

            text_value = getattr(block, "text", None)
            if isinstance(text_value, str):
                text_parts.append(text_value)

        raw_json = "".join(text_parts).strip()
        parsed: object = json.loads(raw_json)

        if not isinstance(parsed, list):
            raise ValueError("LLM extractor must return a JSON list.")

        validated_items: list[dict[str, Any]] = []
        for item in parsed:
            if not isinstance(item, dict):
                raise ValueError("Each extracted pricing item must be a JSON object.")
            validated_items.append(cast(dict[str, Any], item))

        return validated_items