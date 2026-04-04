import sqlite3

from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository
from apps.storage_mcp.tools.store_parsed_prices import store_parsed_prices_tool


def build_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_name TEXT NOT NULL UNIQUE
        );
        CREATE TABLE provider_model_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_id INTEGER NOT NULL,
            model_id INTEGER NOT NULL,
            input_price_per_1m REAL,
            output_price_per_1m REAL,
            currency TEXT NOT NULL DEFAULT 'USD',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    return connection


def test_store_parsed_prices_normalizes_model_names() -> None:
    connection = build_connection()
    provider_repository = ProviderRepository(connection)
    model_repository = ModelRepository(connection)
    price_repository = PriceRepository(connection)

    result = store_parsed_prices_tool(
        provider_repository=provider_repository,
        model_repository=model_repository,
        price_repository=price_repository,
        records=[
            {
                "provider_name": "groq",
                "model_name": "Llama-3.3-70B",
                "input_price_per_1m": 0.59,
                "output_price_per_1m": 0.79,
                "currency": "usd",
            }
        ],
    )

    assert result["success"] is True
    assert result["records"][0]["model_name"] == "llama 3.3 70b"