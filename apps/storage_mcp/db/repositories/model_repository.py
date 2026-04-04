from __future__ import annotations

import re
import sqlite3

from apps.storage_mcp.db.repositories.repository import Repository


class ModelRepository(Repository):
    """Handles model persistence and alias normalization."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__(connection)

    def get_or_create(self, model_name: str) -> int:
        canonical_name = self.normalize_model_name(model_name)

        row = self._connection.execute(
            "SELECT id FROM models WHERE canonical_name = ?",
            (canonical_name,),
        ).fetchone()

        if row is not None:
            return int(row["id"])

        cursor = self._connection.execute(
            "INSERT INTO models (canonical_name) VALUES (?)",
            (canonical_name,),
        )
        self._connection.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to insert model.")

        return int(cursor.lastrowid)

    @staticmethod
    def normalize_model_name(model_name: str) -> str:
        normalized = model_name.strip().lower()
        normalized = normalized.replace("_", " ").replace("-", " ")
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized