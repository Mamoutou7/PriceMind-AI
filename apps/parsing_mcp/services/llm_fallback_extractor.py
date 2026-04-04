from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from core.settings import get_settings


class LLMFallbackExtractor:
    """Uses OpenAI as a fallback extractor when deterministic parsing fails."""

    def __init__(self, client: OpenAI | None = None) -> None:
        self._client = client

    def is_available(self) -> bool:
        """Return True when the fallback LLM is configured."""
        return get_settings().llm_fallback_enabled

    def extract(self, provider_name: str, raw_content: str) -> list[dict[str, Any]]:
        settings = get_settings()

        if not settings.llm_fallback_enabled:
            raise RuntimeError(
                "LLM fallback is not configured. "
                "Set OPENAI_API_KEY and OPENAI_BASE_URL to enable it."
            )

        client = self._client or OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

        prompt = f"""
            Extract pricing data from the following provider page.

            Rules:
            - Return ONLY valid JSON.
            - Return a JSON array.
            - Each item must contain:
              provider_name, model_name, input_price_per_1m, output_price_per_1m, currency
            - Use null when a price is missing.
            - Normalize provider_name to lowercase.
            - Normalize model_name to lowercase.

            Provider: {provider_name}

            Content:
            {raw_content[:12000]}
            """.strip()

        response = client.responses.create(
            model=settings.model_name,
            input=prompt,
        )

        raw_text = (response.output_text or "").strip()
        cleaned_text = self._extract_json_array(raw_text)

        try:
            data = json.loads(cleaned_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Failed to parse JSON from OpenAI response: {raw_text[:500]}"
            ) from exc

        if not isinstance(data, list):
            raise ValueError(f"Expected JSON array, got: {type(data).__name__}")

        normalized_records: list[dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Each JSON item must be an object, got: {type(item).__name__}"
                )

            normalized_records.append(
                {
                    "provider_name": (
                        str(item.get("provider_name")).strip().lower()
                        if item.get("provider_name") is not None
                        else provider_name.strip().lower()
                    ),
                    "model_name": (
                        str(item.get("model_name")).strip().lower()
                        if item.get("model_name") is not None
                        else None
                    ),
                    "input_price_per_1m": item.get("input_price_per_1m"),
                    "output_price_per_1m": item.get("output_price_per_1m"),
                    "currency": (
                        str(item.get("currency")).strip().upper()
                        if item.get("currency") is not None
                        else "USD"
                    ),
                    "extraction_method": "llm",
                    "confidence": 0.60,
                }
            )

        return normalized_records

    @staticmethod
    def _extract_json_array(text: str) -> str:
        """
        Extract a JSON array from model output.

        Handles raw JSON, fenced code blocks, and extra prefix/suffix text.
        """
        text = text.strip()

        fenced_match = re.match(
            r"^```(?:json)?\s*(.*?)\s*```$",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced_match:
            text = fenced_match.group(1).strip()

        start = text.find("[")
        end = text.rfind("]")

        if start == -1 or end == -1 or end < start:
            raise ValueError(f"No JSON array found in OpenAI response: {text[:500]}")

        return text[start : end + 1]