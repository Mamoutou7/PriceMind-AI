from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from apps.storage_mcp.db.connection import get_connection
from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository
from apps.storage_mcp.tools.compare_prices import compare_prices_tool
from apps.storage_mcp.tools.get_latest_prices import get_latest_prices_tool
from apps.storage_mcp.tools.store_parsed_prices import store_parsed_prices_tool
from apps.storage_mcp.tools.upsert_provider_price import upsert_provider_price_tool

mcp = FastMCP("storage_mcp")


def _build_repositories():
    connection = get_connection()
    return (
        connection,
        ProviderRepository(connection),
        ModelRepository(connection),
        PriceRepository(connection),
    )


@mcp.tool(name="store_parsed_prices")
def store_parsed_prices(records: list[dict]) -> dict:
    connection, provider_repository, model_repository, price_repository = _build_repositories()
    try:
        return store_parsed_prices_tool(
            provider_repository=provider_repository,
            model_repository=model_repository,
            price_repository=price_repository,
            records=records,
        )
    finally:
        connection.close()


@mcp.tool(name="upsert_provider_price")
def upsert_provider_price(
    provider_name: str,
    model_name: str,
    input_price_per_1m: float | None = None,
    output_price_per_1m: float | None = None,
    currency: str = "USD",
) -> dict:
    connection, provider_repository, model_repository, price_repository = _build_repositories()
    try:
        return upsert_provider_price_tool(
            provider_repository=provider_repository,
            model_repository=model_repository,
            price_repository=price_repository,
            provider_name=provider_name,
            model_name=model_name,
            input_price_per_1m=input_price_per_1m,
            output_price_per_1m=output_price_per_1m,
            currency=currency,
        )
    finally:
        connection.close()


@mcp.tool(name="get_latest_prices")
def get_latest_prices(limit: int = 10) -> dict:
    connection, _, _, price_repository = _build_repositories()
    try:
        return get_latest_prices_tool(
            price_repository=price_repository,
            limit=limit,
        )
    finally:
        connection.close()


@mcp.tool(name="compare_prices")
def compare_prices(providers: list[str], model_name: str) -> dict:
    connection, _, _, price_repository = _build_repositories()
    try:
        return compare_prices_tool(
            price_repository=price_repository,
            providers=providers,
            model_name=model_name,
        )
    finally:
        connection.close()


if __name__ == "__main__":
    mcp.run(transport="stdio")