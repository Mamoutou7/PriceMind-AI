from pathlib import Path

from apps.scraping_mcp.services.firecrawl_service import FirecrawlService
from apps.scraping_mcp.services.metadata_service import MetadataService
from apps.scraping_mcp.services.raw_document_service import RawDocumentService
from apps.scraping_mcp.services.scrape_service import ScrapeService

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
METADATA_PATH = DATA_DIR / "scraped_metadata.json"

firecrawl_service = FirecrawlService()
raw_document_service = RawDocumentService(DATA_DIR)
metadata_service = MetadataService(METADATA_PATH)

service = ScrapeService(
    firecrawl_service=firecrawl_service,
    raw_document_service=raw_document_service,
    metadata_service=metadata_service,
)

result = service.scrape_provider(
    provider_name="deepinfra",
    url="https://deepinfra.com/pricing",
)

print(result)