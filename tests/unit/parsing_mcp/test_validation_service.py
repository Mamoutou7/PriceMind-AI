import pytest

from apps.parsing_mcp.services.validation_service import ValidationService
from apps.parsing_mcp.models.pricing import ParsedPricingRecord


@pytest.mark.unit
def test_validation_service_requires_at_least_one_price() -> None:
    service = ValidationService()

    with pytest.raises(ValueError, match="At least one price"):
        service.validate_pricing_record(
            {
                "provider_name": "groq",
                "model_name": "llama 3.3 70b",
                "input_price_per_1m": None,
                "output_price_per_1m": None,
            }
        )


def test_currency_symbol_dollar_is_normalized_to_usd() -> None:
    record = ParsedPricingRecord(
        provider_name="fireworks",
        model_name="llama 3.3 70b",
        input_price_per_1m=0.5,
        currency="$",
    )

    assert record.currency == "USD"
