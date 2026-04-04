from pathlib import Path

import pytest

from apps.scraping_mcp.services.firecrawl_service import FirecrawlService
from apps.scraping_mcp.services.metadata_service import MetadataService
from apps.scraping_mcp.services.raw_document_service import RawDocumentService
from apps.scraping_mcp.services.scrape_service import ScrapeService
from apps.scraping_mcp.tools.get_raw_provider_content import (
    get_raw_provider_content_tool,
)
from core.settings import get_settings


@pytest.mark.integration
def test_scraping_pipeline_live(tmp_path: Path) -> None:
    settings = get_settings()
    if not settings.firecrawl_api_key:
        pytest.skip("FIRECRAWL_API_KEY is required for live scraping test.")

    data_dir = tmp_path / "raw"
    metadata_path = data_dir / "scraped_metadata.json"

    firecrawl_service = FirecrawlService()
    raw_document_service = RawDocumentService(base_directory=data_dir)
    metadata_service = MetadataService(metadata_path=metadata_path)
    scrape_service = ScrapeService(
        firecrawl_service=firecrawl_service,
        raw_document_service=raw_document_service,
        metadata_service=metadata_service,
    )

    scrape_result = scrape_service.scrape_provider(
        provider_name="deepinfra",
        url="https://deepinfra.com/pricing",
    )

    assert scrape_result["success"] is True

    raw_result = get_raw_provider_content_tool(
        provider_name="deepinfra",
        base_directory=data_dir,
    )

    assert raw_result["success"] is True
    assert raw_result.get("markdown") or raw_result.get("html")