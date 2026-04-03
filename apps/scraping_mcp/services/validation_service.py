from __future__ import annotations

from typing import Any


class ValidationService:
    """Validates extracted pricing records."""

    REQUIRED_FIELDS = {"provider_name", "model_name"}

    def validate_pricing_record(self, record: dict[str, Any]) -> dict[str, Any]:
        missing_fields = self.REQUIRED_FIELDS - record.keys()
        if missing_fields:
            raise ValueError(f"Missing required fields: {sorted(missing_fields)}")

        validated = dict(record)
        validated["provider_name"] = str(validated["provider_name"]).strip().lower()
        validated["model_name"] = str(validated["model_name"]).strip()

        for price_field in ("input_price_per_1m", "output_price_per_1m"):
            value = validated.get(price_field)
            if value is None or value == "":
                continue
            validated[price_field] = float(value)

        validated["currency"] = str(validated.get("currency", "USD")).strip().upper()
        return validated

    def validate_record(self, record: dict[str, Any]) -> dict[str, Any]:
        return self.validate_pricing_record(record)