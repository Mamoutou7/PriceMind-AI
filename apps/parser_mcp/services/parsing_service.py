from __future__ import annotations

import re
from typing import Any

from apps.parser_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parser_mcp.services.validation_service import ValidationService


class ParsingService:
    """Parses raw provider content into normalized pricing records."""

    def __init__(
        self,
        validation_service: ValidationService,
        llm_fallback_extractor: LLMFallbackExtractor,
    ) -> None:
        self._validation_service = validation_service
        self._llm_fallback_extractor = llm_fallback_extractor

    def parse_document(
        self,
        provider_name: str,
        raw_content: str,
    ) -> list[dict[str, Any]]:
        records = self._parse_deterministically(
            provider_name=provider_name,
            raw_content=raw_content,
        )

        if not records:
            records = self._llm_fallback_extractor.extract(
                provider_name=provider_name,
                raw_content=raw_content,
            )

        return [self._validation_service.validate_pricing_record(record) for record in records]

    @staticmethod
    def _parse_deterministically(
        provider_name: str,
        raw_content: str,
    ) -> list[dict[str, Any]]:
        pattern = re.compile(
            r"(?P<model>[A-Za-z0-9\-\s]+?)\s+"
            r"(?P<input>\d+(?:\.\d+)?)\s*/\s*1M\s+input.*?"
            r"(?P<output>\d+(?:\.\d+)?)\s*/\s*1M\s+output",
            flags=re.IGNORECASE | re.DOTALL,
        )

        records: list[dict[str, Any]] = []

        for match in pattern.finditer(raw_content):
            records.append(
                {
                    "provider_name": provider_name,
                    "model_name": match.group("model").strip(),
                    "input_price_per_1m": match.group("input"),
                    "output_price_per_1m": match.group("output"),
                    "currency": "USD",
                }
            )

        return records