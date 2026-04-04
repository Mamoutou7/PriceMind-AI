import sqlite3

from apps.storage_mcp.db.repositories.model_repository import ModelRepository


def build_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE models "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, canonical_name TEXT NOT NULL UNIQUE)"
    )
    return connection


def test_model_repository_normalizes_aliases() -> None:
    connection = build_connection()
    repository = ModelRepository(connection)

    first_id = repository.get_or_create("Llama-3.3-70B")
    second_id = repository.get_or_create("llama 3.3 70b")

    assert first_id == second_id
