from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "data" / "db"
DB_PATH = DB_DIR / "pricing.sqlite"


SCHEMA = """
CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS provider_model_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    input_price_per_1m REAL,
    output_price_per_1m REAL,
    currency TEXT NOT NULL DEFAULT 'USD',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (provider_id) REFERENCES providers(id),
    FOREIGN KEY (model_id) REFERENCES models(id)
);

CREATE INDEX IF NOT EXISTS idx_provider_model_prices_created_at
ON provider_model_prices(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_provider_model_prices_provider_id
ON provider_model_prices(provider_id);

CREATE INDEX IF NOT EXISTS idx_provider_model_prices_model_id
ON provider_model_prices(model_id);
"""


def main() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    try:
        connection.executescript(SCHEMA)
        connection.commit()
        print(f"Database initialized at: {DB_PATH}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
