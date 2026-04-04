from __future__ import annotations

import sqlite3
from typing import Any

from apps.storage_mcp.db.repositories.repository import Repository


class PriceRepository(Repository):
    """Handles price persistence and retrieval."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__(connection)

    def upsert_price(
        self,
        provider_id: int,
        model_id: int,
        input_price_per_1m: float | None,
        output_price_per_1m: float | None,
        currency: str,
    ) -> int:
        cursor = self._connection.execute(
            """
            INSERT INTO provider_model_prices (
                provider_id,
                model_id,
                input_price_per_1m,
                output_price_per_1m,
                currency
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                provider_id,
                model_id,
                input_price_per_1m,
                output_price_per_1m,
                currency,
            ),
        )
        self._connection.commit()

        if cursor.lastrowid is None:
            raise RuntimeError("Failed to insert provider model price.")

        return int(cursor.lastrowid)

    def insert_price(
        self,
        provider_id: int,
        model_id: int,
        input_price_per_1m: float | None,
        output_price_per_1m: float | None,
        currency: str,
    ) -> int:
        """Backward-compatible alias used by older tests/scripts."""
        return self.upsert_price(
            provider_id=provider_id,
            model_id=model_id,
            input_price_per_1m=input_price_per_1m,
            output_price_per_1m=output_price_per_1m,
            currency=currency,
        )

    def get_latest_prices(self, limit: int = 10) -> list[dict[str, Any]]:
        cursor = self._connection.execute(
            """
            SELECT
                p.name AS provider_name,
                m.canonical_name AS model_name,
                ppm.input_price_per_1m,
                ppm.output_price_per_1m,
                ppm.currency,
                ppm.created_at
            FROM provider_model_prices AS ppm
            INNER JOIN providers AS p ON ppm.provider_id = p.id
            INNER JOIN models AS m ON ppm.model_id = m.id
            ORDER BY ppm.created_at DESC, ppm.id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def compare_prices(
        self,
        providers: list[str],
        model_name: str,
    ) -> list[dict[str, Any]]:
        if not providers:
            return []

        normalized_providers = [provider.strip().lower() for provider in providers]
        placeholders = ", ".join("?" for _ in normalized_providers)

        query = f"""
            SELECT
                p.name AS provider_name,
                m.canonical_name AS model_name,
                ppm.input_price_per_1m,
                ppm.output_price_per_1m,
                ppm.currency,
                ppm.created_at
            FROM provider_model_prices AS ppm
            INNER JOIN providers AS p ON ppm.provider_id = p.id
            INNER JOIN models AS m ON ppm.model_id = m.id
            WHERE p.name IN ({placeholders})
              AND LOWER(m.canonical_name) = LOWER(?)
            ORDER BY ppm.created_at DESC, ppm.id DESC
        """

        cursor = self._connection.execute(query, (*normalized_providers, model_name))
        rows = cursor.fetchall()

        latest_by_provider: dict[str, dict[str, Any]] = {}
        for row in rows:
            record = dict(row)
            provider_name = str(record["provider_name"])
            if provider_name not in latest_by_provider:
                latest_by_provider[provider_name] = record

        return list(latest_by_provider.values())