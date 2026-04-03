from pathlib import Path

from apps.scraping_mcp.services.firecrawl_service import FirecrawlService
from apps.scraping_mcp.services.metadata_service import MetadataService
from apps.scraping_mcp.services.raw_document_service import RawDocumentService
from apps.scraping_mcp.services.scrape_service import ScrapeService
from apps.scraping_mcp.tools.get_raw_provider_content import (
    get_raw_provider_content_tool,
)
from apps.parser_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parser_mcp.services.parsing_service import ParsingService
from apps.parser_mcp.services.validation_service import ValidationService
from apps.storage_mcp.db.connection import get_connection
from apps.storage_mcp.db.repositories.model_repository import ModelRepository
from apps.storage_mcp.db.repositories.price_repository import PriceRepository
from apps.storage_mcp.db.repositories.provider_repository import ProviderRepository
from apps.storage_mcp.tools.store_parsed_prices import store_parsed_prices_tool

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
METADATA_PATH = DATA_DIR / "scraped_metadata.json"
DB_PATH = BASE_DIR / "data" / "db" / "pricing.sqlite"

# Scrape
scrape_service = ScrapeService(
    firecrawl_service=FirecrawlService(),
    raw_document_service=RawDocumentService(DATA_DIR),
    metadata_service=MetadataService(METADATA_PATH),
)

scrape_result = scrape_service.scrape_provider(
    provider_name="deepinfra",
    url="https://deepinfra.com/pricing",
)
print("SCRAPE RESULT:", scrape_result["success"])

# Read raw content
raw_result = get_raw_provider_content_tool(
    provider_name="deepinfra",
    base_directory=DATA_DIR,
)
print("RAW RESULT:", raw_result["success"])

# Parse
parsing_service = ParsingService(
    validation_service=ValidationService(),
    llm_fallback_extractor=LLMFallbackExtractor(),
)

records = parsing_service.parse_document(
    provider_name="deepinfra",
    raw_content=raw_result.get("markdown") or raw_result.get("html", ""),
)
print("PARSED RECORDS:", len(records))

# Store
connection = get_connection(DB_PATH)
provider_repository = ProviderRepository(connection)
model_repository = ModelRepository(connection)
price_repository = PriceRepository(connection)

store_result = store_parsed_prices_tool(
    provider_repository=provider_repository,
    model_repository=model_repository,
    price_repository=price_repository,
    records=records,
)
print("STORE RESULT:", store_result)

connection.close()