from typing import Any


def compare_prices(
    self,
    providers: list[str],
    model_name: str,
) -> list[dict[str, Any]]:
    if not providers:
        return []

    normalized_providers = [provider.strip().lower() for provider in providers]
    placeholders = ", ".join("?" for _ in normalized_providers)

    # The number of placeholders is derived only from the trusted list length,
    # while all actual values are still passed as SQL parameters.
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
