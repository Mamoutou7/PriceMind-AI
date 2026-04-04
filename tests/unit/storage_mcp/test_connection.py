from pathlib import Path

import pytest

from apps.storage_mcp.db.connection import get_connection

pytestmark = pytest.mark.unit


def test_connection_creates_db(tmp_path: Path):
    db = tmp_path / "test.sqlite"

    conn = get_connection(db)

    assert db.exists()
    conn.close()
