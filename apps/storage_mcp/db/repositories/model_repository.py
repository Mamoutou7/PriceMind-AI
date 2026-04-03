from __future__ import annotations

import sqlite3


class ModelRepository:
    """Handles model persistence."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def get_or_create(self, model_name: str) -> int:
        normalized_name = model_name.strip()

        cursor = self._connection.execute(
            "SELECT id FROM models WHERE canonical_name = ?",
            (normalized_name,),
        )
        row = cursor.fetchone()
        if row is not None:
            return int(row["id"])

        cursor = self._connection.execute(
            "INSERT INTO models (canonical_name) VALUES (?)",
            (normalized_name,),
        )
        self._connection.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to insert model.")

        return cursor.lastrowid
