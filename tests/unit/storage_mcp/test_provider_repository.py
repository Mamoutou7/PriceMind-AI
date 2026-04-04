import sqlite3

from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository


def build_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE providers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE)"
    )
    return connection


def test_provider_repository_reuses_existing_provider() -> None:
    connection = build_connection()
    repository = ProviderRepository(connection)

    first_id = repository.get_or_create("groq")
    second_id = repository.get_or_create("groq")

    assert first_id == second_id