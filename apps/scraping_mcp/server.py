from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from apps.scraping_mcp.services.firecrawl_service import FirecrawlService
from apps.scraping_mcp.services.metadata_service import MetadataService
from apps.scraping_mcp.services.raw_document_service import RawDocumentService
from apps.scraping_mcp.services.scrape_service import ScrapeService
from apps.scraping_mcp.tools.get_raw_provider_content import (
    get_raw_provider_content_tool,
)
from apps.scraping_mcp.tools.get_scrape_result import get_scrape_result_tool
from apps.scraping_mcp.tools.scrape_all_providers import scrape_all_providers_tool
from apps.scraping_mcp.tools.scrape_provider import scrape_provider_tool

mcp = FastMCP("scraping_mcp")

firecrawl_service = FirecrawlService()
raw_document_service = RawDocumentService()
metadata_service = MetadataService()
scrape_service = ScrapeService(
    firecrawl_service=firecrawl_service,
    raw_document_service=raw_document_service,
    metadata_service=metadata_service,
)


@mcp.tool(name="scrape_provider")
def scrape_provider(
    provider_name: str, url: str, formats: list[str] | None = None
) -> dict:
    return scrape_provider_tool(
        scrape_service=scrape_service,
        provider_name=provider_name,
        url=url,
        formats=formats,
    )


@mcp.tool(name="scrape_all_providers")
def scrape_all_providers(formats: list[str] | None = None) -> dict:
    return scrape_all_providers_tool(
        scrape_service=scrape_service,
        formats=formats,
    )


@mcp.tool(name="get_scrape_result")
def get_scrape_result(provider_name: str) -> dict:
    return get_scrape_result_tool(
        metadata_service=metadata_service,
        provider_name=provider_name,
    )


@mcp.tool(name="get_raw_provider_content")
def get_raw_provider_content(provider_name: str) -> dict:
    return get_raw_provider_content_tool(provider_name=provider_name)


if __name__ == "__main__":
    mcp.run(transport="stdio")
