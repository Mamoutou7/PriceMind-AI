from __future__ import annotations

import re
from typing import Any

from apps.parsing_mcp.models.pricing import (
    ExtractionMetadata,
    ParsedPricingRecord,
    ParsingResult,
)
from apps.parsing_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parsing_mcp.services.validation_service import ValidationService


class ParsingService:
    """Parses provider pricing pages with d
    eterministic extraction first, then LLM fallback.
    """

    PRICE_PATTERN = re.compile(
        r"(?P<value>\d+(?:\.\d+)?)\s*(?:/|per)?\s*1m",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        validation_service: ValidationService,
        llm_fallback_extractor: LLMFallbackExtractor,
    ) -> None:
        self._validation_service = validation_service
        self._llm_fallback_extractor = llm_fallback_extractor

    def parse_document(self, provider_name: str, raw_content: str) -> ParsingResult:
        normalized_provider = provider_name.strip().lower()
        deterministic_records = self._deterministic_extract(
            normalized_provider, raw_content
        )

        if deterministic_records:
            validated = self._validate_records(deterministic_records)
            return ParsingResult(
                records=validated,
                metadata=ExtractionMetadata(
                    provider_name=normalized_provider,
                    used_fallback=False,
                    extraction_method="deterministic",
                    raw_content_length=len(raw_content),
                    record_count=len(validated),
                ),
            )

        if self._llm_fallback_extractor.is_available():
            llm_records = self._llm_fallback_extractor.extract(
                normalized_provider, raw_content
            )
            validated = self._validate_records(llm_records)
            return ParsingResult(
                records=validated,
                metadata=ExtractionMetadata(
                    provider_name=normalized_provider,
                    used_fallback=True,
                    extraction_method="llm",
                    raw_content_length=len(raw_content),
                    record_count=len(validated),
                ),
            )

        return ParsingResult(
            records=[],
            metadata=ExtractionMetadata(
                provider_name=normalized_provider,
                used_fallback=False,
                extraction_method="none",
                raw_content_length=len(raw_content),
                record_count=0,
            ),
        )

    def _validate_records(
        self, records: list[dict[str, Any]]
    ) -> list[ParsedPricingRecord]:
        validated: list[ParsedPricingRecord] = []
        seen: set[tuple[str, str, float | None, float | None, str]] = set()

        for raw_record in records:
            record = self._validation_service.validate_pricing_record(raw_record)
            key = (
                record.provider_name,
                record.model_name,
                record.input_price_per_1m,
                record.output_price_per_1m,
                record.currency,
            )
            if key not in seen:
                seen.add(key)
                validated.append(record)

        return validated

    def _deterministic_extract(
        self, provider_name: str, raw_content: str
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []

        records.extend(self._extract_from_markdown_tables(provider_name, raw_content))
        records.extend(self._extract_from_inline_lines(provider_name, raw_content))

        return records

    def _extract_from_markdown_tables(
        self, provider_name: str, raw_content: str
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        lines = [line.strip() for line in raw_content.splitlines() if line.strip()]

        for index, line in enumerate(lines):
            if "|" not in line:
                continue

            columns = [cell.strip().lower() for cell in line.strip("|").split("|")]
            if len(columns) < 3:
                continue

            header_text = " | ".join(columns)
            if "model" not in header_text:
                continue
            if not any(
                keyword in header_text for keyword in ("input", "output", "price")
            ):
                continue

            if index + 1 >= len(lines):
                continue

            separator_candidate = lines[index + 1]
            if "|" not in separator_candidate:
                continue

            data_index = index + 2
            while data_index < len(lines) and "|" in lines[data_index]:
                row_cells = [
                    cell.strip() for cell in lines[data_index].strip("|").split("|")
                ]
                if len(row_cells) < len(columns):
                    data_index += 1
                    continue

                row_map = {
                    columns[cell_index]: row_cells[cell_index]
                    for cell_index in range(min(len(columns), len(row_cells)))
                }

                model_name = self._resolve_model_name_from_row(row_map)
                if not model_name:
                    data_index += 1
                    continue

                input_price = self._resolve_price_from_row(row_map, ("input",))
                output_price = self._resolve_price_from_row(row_map, ("output",))

                if input_price is None and output_price is None:
                    data_index += 1
                    continue

                records.append(
                    {
                        "provider_name": provider_name,
                        "model_name": model_name,
                        "input_price_per_1m": input_price,
                        "output_price_per_1m": output_price,
                        "currency": "USD",
                        "extraction_method": "deterministic",
                        "confidence": 0.95,
                    }
                )
                data_index += 1

        return records

    def _extract_from_inline_lines(
        self, provider_name: str, raw_content: str
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []

        for line in raw_content.splitlines():
            cleaned = " ".join(line.strip().split())
            if not cleaned:
                continue

            lower_line = cleaned.lower()
            if "input" not in lower_line and "output" not in lower_line:
                continue

            prices = [
                float(match.group("value"))
                for match in self.PRICE_PATTERN.finditer(cleaned)
            ]
            if not prices:
                continue

            model_name = self._extract_model_name_from_line(cleaned)
            if not model_name:
                continue

            input_price = prices[0] if len(prices) >= 1 else None
            output_price = prices[1] if len(prices) >= 2 else None

            records.append(
                {
                    "provider_name": provider_name,
                    "model_name": model_name,
                    "input_price_per_1m": input_price,
                    "output_price_per_1m": output_price,
                    "currency": "USD",
                    "extraction_method": "deterministic",
                    "confidence": 0.85,
                }
            )

        return records

    @staticmethod
    def _resolve_model_name_from_row(row_map: dict[str, str]) -> str | None:
        for key, value in row_map.items():
            lowered_key = key.lower()
            if "model" in lowered_key or "name" in lowered_key:
                normalized = value.strip().lower()
                return normalized or None
        return None

    @classmethod
    def _resolve_price_from_row(
        cls, row_map: dict[str, str], keywords: tuple[str, ...]
    ) -> float | None:
        for key, value in row_map.items():
            lowered_key = key.lower()
            if any(keyword in lowered_key for keyword in keywords):
                match = cls.PRICE_PATTERN.search(value.lower())
                if match:
                    return float(match.group("value"))
                try:
                    return float(value.strip().replace("$", ""))
                except ValueError:
                    continue
        return None

    @classmethod
    def _extract_model_name_from_line(cls, line: str) -> str | None:
        lower_line = line.lower()
        for token in (
            " input",
            " output",
            " $",
            " 0.",
            " 1.",
            " 2.",
            " 3.",
            " 4.",
            " 5.",
        ):
            index = lower_line.find(token)
            if index > 0:
                candidate = line[:index].strip(" :-|")
                if candidate:
                    return candidate.lower()
        return None
