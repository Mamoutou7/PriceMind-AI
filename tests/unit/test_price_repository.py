import sqlite3

from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository


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


def test_insert_and_read_latest_prices() -> None:
    connection = build_connection()

    provider_repository = ProviderRepository(connection)
    model_repository = ModelRepository(connection)
    price_repository = PriceRepository(connection)

    provider_id = provider_repository.get_or_create("deepinfra")
    model_id = model_repository.get_or_create("DeepSeek V3")

    price_repository.upsert_price(
        provider_id=provider_id,
        model_id=model_id,
        input_price_per_1m=0.27,
        output_price_per_1m=1.10,
        currency="USD",
    )

    rows = price_repository.get_latest_prices(limit=5)

    assert len(rows) == 1
    assert rows[0]["provider_name"] == "deepinfra"
    assert rows[0]["model_name"] == "DeepSeek V3"