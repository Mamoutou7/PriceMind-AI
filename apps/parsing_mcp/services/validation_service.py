from __future__ import annotations

from typing import Any

from apps.parsing_mcp.models.pricing import ParsedPricingRecord


class ValidationService:
    """Validates extracted pricing payloads before persistence."""

    def validate_pricing_record(
        self, raw_record: dict[str, Any]
    ) -> ParsedPricingRecord:
        record = ParsedPricingRecord.model_validate(raw_record)

        if record.input_price_per_1m is None and record.output_price_per_1m is None:
            raise ValueError("At least one price must be present.")

        if record.input_price_per_1m is not None and record.input_price_per_1m < 0:
            raise ValueError("Input price must be non-negative.")

        if record.output_price_per_1m is not None and record.output_price_per_1m < 0:
            raise ValueError("Output price must be non-negative.")

        return record
