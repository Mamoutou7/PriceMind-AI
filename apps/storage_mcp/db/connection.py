from __future__ import annotations

import sqlite3
from pathlib import Path

from core.config import DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    target_path = db_path or DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(target_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    schema_path = Path(__file__).resolve().parent / "schema.sql"
    connection.executescript(schema_path.read_text(encoding="utf-8"))
    connection.commit()

    return connection
