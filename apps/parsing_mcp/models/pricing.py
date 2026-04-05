from __future__ import annotations

from collections.abc import Iterator
from typing import Literal, overload

from pydantic import BaseModel, Field, field_validator


class ParsedPricingRecord(BaseModel):
    """Normalized pricing record extracted from a provider document."""

    provider_name: str = Field(min_length=1)
    model_name: str = Field(min_length=1)

    input_price_per_1m: float | None = None
    output_price_per_1m: float | None = None

    currency: str = Field(default="USD", min_length=3, max_length=3)

    extraction_method: Literal["deterministic", "llm"] = "deterministic"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("provider_name", "model_name")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> str:
        if value is None:
            return "USD"

        normalized = str(value).strip().upper()

        symbol_map = {
            "$": "USD",
            "€": "EUR",
            "£": "GBP",
        }

        if normalized in symbol_map:
            return symbol_map[normalized]

        if not normalized:
            return "USD"

        return normalized

    @field_validator("input_price_per_1m", "output_price_per_1m", mode="before")
    @classmethod
    def normalize_optional_prices(cls, value: object) -> float | None:
        if value in (None, ""):
            return None
        return float(value)


class ExtractionMetadata(BaseModel):
    """Metadata about how parsing/extraction was performed."""

    provider_name: str = Field(min_length=1)
    used_fallback: bool = False
    extraction_method: Literal["deterministic", "llm", "none"] = "none"
    raw_content_length: int = Field(ge=0)
    record_count: int = Field(ge=0)


class ParsingResult(BaseModel):
    """Structured result returned by the parsing pipeline."""

    records: list[ParsedPricingRecord] = Field(default_factory=list)
    metadata: ExtractionMetadata

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self) -> Iterator[ParsedPricingRecord]:
        return iter(self.records)

    @overload
    def __getitem__(self, index: int) -> ParsedPricingRecord: ...

    @overload
    def __getitem__(self, index: slice) -> list[ParsedPricingRecord]: ...

    def __getitem__(self, index: int | slice) -> ParsedPricingRecord | list[ParsedPricingRecord]:
        return self.records[index]