from __future__ import annotations

from typing import Any


class ValidationService:
    """Validates and normalizes extracted pricing records."""

    REQUIRED_FIELDS = {"provider_name", "model_name"}

    def validate_pricing_record(
        self,
        pricing_record: dict[str, Any],
    ) -> dict[str, Any]:
        missing_fields = self.REQUIRED_FIELDS - set(pricing_record.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {sorted(missing_fields)}")

        normalized_record = dict(pricing_record)

        normalized_record["provider_name"] = (
            str(normalized_record["provider_name"]).strip().lower()
        )

        normalized_record["model_name"] = (
            str(normalized_record["model_name"]).strip().lower()
        )

        for field_name in ("input_price_per_1m", "output_price_per_1m"):
            value = normalized_record.get(field_name)
            if value is None or value == "":
                normalized_record[field_name] = None
                continue

            normalized_record[field_name] = float(value)

        normalized_record["currency"] = (
            str(normalized_record.get("currency", "USD")).strip().upper()
        )

        return normalized_record
