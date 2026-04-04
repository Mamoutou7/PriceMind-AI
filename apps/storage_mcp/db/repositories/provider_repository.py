from __future__ import annotations

import sqlite3

from apps.storage_mcp.db.repositories.repository import Repository


class ProviderRepository(Repository):
    """Handles provider persistence and lookup."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__(connection)

    def get_or_create(self, provider_name: str) -> int:
        normalized_name = provider_name.strip().lower()

        row = self._connection.execute(
            "SELECT id FROM providers WHERE name = ?",
            (normalized_name,),
        ).fetchone()

        if row is not None:
            return int(row["id"])

        cursor = self._connection.execute(
            "INSERT INTO providers (name) VALUES (?)",
            (normalized_name,),
        )
        self._connection.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to insert provider.")

        return int(cursor.lastrowid)
