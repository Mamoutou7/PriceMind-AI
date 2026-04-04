from __future__ import annotations

from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository


def compare_prices_tool(
    price_repository: PriceRepository,
    providers: list[str],
    model_name: str,
) -> dict:
    normalized_providers = [provider.strip().lower() for provider in providers]
    normalized_model = ModelRepository.normalize_model_name(model_name)

    return {
        "success": True,
        "data": price_repository.compare_prices(
            providers=normalized_providers,
            model_name=normalized_model,
        ),
    }