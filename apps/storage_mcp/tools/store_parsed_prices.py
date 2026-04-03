from __future__ import annotations

from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository


def store_parsed_prices_tool(
    provider_repository: ProviderRepository,
    model_repository: ModelRepository,
    price_repository: PriceRepository,
    records: list[dict],
) -> dict:
    inserted_ids: list[int] = []

    for record in records:
        provider_name = str(record["provider_name"]).strip().lower()
        model_name = str(record["model_name"]).strip().lower()
        input_price = record.get("input_price_per_1m")
        output_price = record.get("output_price_per_1m")
        currency = str(record.get("currency", "USD")).strip().upper()

        provider_id = provider_repository.get_or_create(provider_name)
        model_id = model_repository.get_or_create(model_name)

        price_id = price_repository.upsert_price(
            provider_id=provider_id,
            model_id=model_id,
            input_price_per_1m=input_price,
            output_price_per_1m=output_price,
            currency=currency,
        )
        inserted_ids.append(price_id)

    return {
        "success": True,
        "inserted_count": len(inserted_ids),
        "price_ids": inserted_ids,
    }