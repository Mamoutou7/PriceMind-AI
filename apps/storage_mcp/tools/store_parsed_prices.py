from __future__ import annotations

from typing import Any

from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository


def store_parsed_prices_tool(
    provider_repository: ProviderRepository,
    model_repository: ModelRepository,
    price_repository: PriceRepository,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    stored_records: list[dict[str, Any]] = []

    for record in records:
        provider_name = str(record["provider_name"]).strip().lower()
        model_name = ModelRepository.normalize_model_name(str(record["model_name"]))
        currency = str(record.get("currency", "USD")).strip().upper()

        provider_id = provider_repository.get_or_create(provider_name)
        model_id = model_repository.get_or_create(model_name)

        price_repository.upsert_price(
            provider_id=provider_id,
            model_id=model_id,
            input_price_per_1m=record.get("input_price_per_1m"),
            output_price_per_1m=record.get("output_price_per_1m"),
            currency=currency,
        )

        stored_records.append(
            {
                "provider_name": provider_name,
                "model_name": model_name,
                "input_price_per_1m": record.get("input_price_per_1m"),
                "output_price_per_1m": record.get("output_price_per_1m"),
                "currency": currency,
            }
        )

    return {
        "success": True,
        "inserted_count": len(stored_records),
        "records": stored_records,
    }
