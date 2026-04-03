from pathlib import Path

from apps.scraping_mcp.services.firecrawl_service import FirecrawlService
from apps.scraping_mcp.services.metadata_service import MetadataService
from apps.scraping_mcp.services.raw_document_service import RawDocumentService
from apps.scraping_mcp.services.scrape_service import ScrapeService
from apps.scraping_mcp.tools.get_raw_provider_content import (
    get_raw_provider_content_tool,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw"
METADATA_PATH = DATA_DIR / "scraped_metadata.json"

firecrawl_service = FirecrawlService()
raw_document_service = RawDocumentService(base_directory=DATA_DIR)
metadata_service = MetadataService(metadata_path=METADATA_PATH)

scrape_service = ScrapeService(
    firecrawl_service=firecrawl_service,
    raw_document_service=raw_document_service,
    metadata_service=metadata_service,
)

scrape_result = scrape_service.scrape_provider(
    provider_name="deepinfra",
    url="https://deepinfra.com/pricing",
)

print("SCRAPE RESULT:")
print(scrape_result)

raw_result = get_raw_provider_content_tool(
    provider_name="deepinfra",
    base_directory=DATA_DIR,
)

print("\nRAW CONTENT RESULT:")
print(
    {
        "success": raw_result["success"],
        "provider_name": raw_result.get("provider_name"),
        "markdown_length": len(raw_result.get("markdown", "")),
        "html_length": len(raw_result.get("html", "")),
    }
)