from __future__ import annotations

from apps.storage_mcp.db.repositories.price_repository import PriceRepository


def get_latest_prices_tool(
    price_repository: PriceRepository,
    limit: int = 10,
) -> dict:
    return {
        "success": True,
        "data": price_repository.get_latest_prices(limit=limit),
    }