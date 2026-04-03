from __future__ import annotations

import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from apps.storage_mcp.db.connection import get_connection
from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository
from apps.storage_mcp.tools.compare_prices import compare_prices_tool
from apps.storage_mcp.tools.get_latest_prices import get_latest_prices_tool
from apps.storage_mcp.tools.store_parsed_prices import store_parsed_prices_tool
from apps.storage_mcp.tools.upsert_provider_price import upsert_provider_price_tool

BASE_DIR = Path(__file__).resolve().parents[2]
DB_DIR = BASE_DIR / "data" / "db"
DB_PATH = DB_DIR / "pricing.sqlite"

mcp = FastMCP("storage_mcp")


def _build_connection() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return get_connection(DB_PATH)


def _build_repositories() -> tuple[
    sqlite3.Connection,
    ProviderRepository,
    ModelRepository,
    PriceRepository,
]:
    connection = _build_connection()
    provider_repository = ProviderRepository(connection)
    model_repository = ModelRepository(connection)
    price_repository = PriceRepository(connection)
    return connection, provider_repository, model_repository, price_repository


@mcp.tool(name="upsert_provider_price")
def upsert_provider_price(
    provider_name: str,
    model_name: str,
    input_price_per_1m: float | None = None,
    output_price_per_1m: float | None = None,
    currency: str = "USD",
) -> dict:
    connection, provider_repository, model_repository, price_repository = (
        _build_repositories()
    )

    try:
        return upsert_provider_price_tool(
            provider_repository=provider_repository,
            model_repository=model_repository,
            price_repository=price_repository,
            provider_name=provider_name.strip().lower(),
            model_name=model_name.strip(),
            input_price_per_1m=input_price_per_1m,
            output_price_per_1m=output_price_per_1m,
            currency=currency.strip().upper(),
        )
    finally:
        connection.close()

@mcp.tool(name="store_parsed_prices")
def store_parsed_prices(records: list[dict]) -> dict:
    connection, provider_repository, model_repository, price_repository = (
        _build_repositories()
    )

    try:
        return store_parsed_prices_tool(
            provider_repository=provider_repository,
            model_repository=model_repository,
            price_repository=price_repository,
            records=records,
        )
    finally:
        connection.close()


@mcp.tool(name="get_latest_prices")
def get_latest_prices(limit: int = 10) -> dict:
    connection, _, _, price_repository = _build_repositories()

    try:
        safe_limit = max(1, min(limit, 100))
        return get_latest_prices_tool(
            price_repository=price_repository,
            limit=safe_limit,
        )
    finally:
        connection.close()

@mcp.tool(name="compare_prices")
def compare_prices(providers: list[str], model_name: str) -> dict:
    connection, _, _, price_repository = _build_repositories()

    try:
        normalized_providers = [provider.strip().lower() for provider in providers]
        return compare_prices_tool(
            price_repository=price_repository,
            providers=normalized_providers,
            model_name=model_name.strip().lower(),
        )
    finally:
        connection.close()

if __name__ == "__main__":
    mcp.run(transport="stdio")
