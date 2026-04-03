from __future__ import annotations

from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository


def upsert_provider_price_tool(
    provider_repository: ProviderRepository,
    model_repository: ModelRepository,
    price_repository: PriceRepository,
    provider_name: str,
    model_name: str,
    input_price_per_1m: float | None,
    output_price_per_1m: float | None,
    currency: str = "USD",
) -> dict:
    provider_id = provider_repository.get_or_create(provider_name)
    model_id = model_repository.get_or_create(model_name)

    price_id = price_repository.upsert_price(
        provider_id=provider_id,
        model_id=model_id,
        input_price_per_1m=input_price_per_1m,
        output_price_per_1m=output_price_per_1m,
        currency=currency,
    )

    return {
        "success": True,
        "price_id": price_id,
        "provider_name": provider_name,
        "model_name": model_name,
    }
