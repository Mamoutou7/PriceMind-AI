from __future__ import annotations

from apps.storage_mcp.db.repositories.price_repository import PriceRepository


def compare_prices_tool(
    price_repository: PriceRepository,
    providers: list[str],
    model_name: str,
) -> dict:
    return {
        "success": True,
        "data": price_repository.compare_prices(
            providers=providers,
            model_name=model_name,
        ),
    }