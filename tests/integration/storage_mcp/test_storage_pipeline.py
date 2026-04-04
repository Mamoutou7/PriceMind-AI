import pytest
from pathlib import Path

from apps.storage_mcp.db.connection import get_connection
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository
from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository

pytestmark = pytest.mark.integration


def test_store_and_fetch(tmp_path: Path):
    conn = get_connection(tmp_path / "db.sqlite")

    provider_repo = ProviderRepository(conn)
    model_repo = ModelRepository(conn)
    price_repo = PriceRepository(conn)

    provider_id = provider_repo.get_or_create("groq")
    model_id = model_repo.get_or_create("llama")

    price_repo.insert_price(provider_id, model_id, 0.5, 0.8, "USD")

    data = price_repo.get_latest_prices(limit=5)

    assert len(data) == 1

    conn.close()