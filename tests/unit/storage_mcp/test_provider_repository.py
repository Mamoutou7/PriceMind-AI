from pathlib import Path

import pytest

from apps.storage_mcp.db.connection import get_connection
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository

pytestmark = pytest.mark.unit


def test_provider_repository_reuses_existing_provider(tmp_path: Path) -> None:
    db = tmp_path / "test.sqlite"
    connection = get_connection(db)
    repository = ProviderRepository(connection)

    first_id = repository.get_or_create("groq")
    second_id = repository.get_or_create("groq")

    assert first_id == second_id

    connection.close()