from pathlib import Path

from apps.storage_mcp.db.connection import get_connection
from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository
from apps.storage_mcp.tools.compare_prices import compare_prices_tool
from apps.storage_mcp.tools.get_latest_prices import get_latest_prices_tool
from apps.storage_mcp.tools.store_parsed_prices import store_parsed_prices_tool

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "db" / "pricing.sqlite"

connection = get_connection(DB_PATH)

provider_repository = ProviderRepository(connection)
model_repository = ModelRepository(connection)
price_repository = PriceRepository(connection)

records = [
    {
        "provider_name": "deepinfra",
        "model_name": "deepseek v3",
        "input_price_per_1m": 0.27,
        "output_price_per_1m": 1.10,
        "currency": "USD",
    },
    {
        "provider_name": "cloudrift",
        "model_name": "deepseek v3",
        "input_price_per_1m": 0.30,
        "output_price_per_1m": 1.25,
        "currency": "USD",
    },
]

store_result = store_parsed_prices_tool(
    provider_repository=provider_repository,
    model_repository=model_repository,
    price_repository=price_repository,
    records=records,
)
print("STORE RESULT:")
print(store_result)

latest_result = get_latest_prices_tool(
    price_repository=price_repository,
    limit=10,
)
print("\nLATEST RESULT:")
print(latest_result)

compare_result = compare_prices_tool(
    price_repository=price_repository,
    providers=["deepinfra", "cloudrift"],
    model_name="deepseek v3",
)
print("\nCOMPARE RESULT:")
print(compare_result)

connection.close()