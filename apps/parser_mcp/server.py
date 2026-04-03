from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from apps.parser_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parser_mcp.services.parsing_service import ParsingService
from apps.parser_mcp.services.validation_service import ValidationService

mcp = FastMCP("parser_mcp")

validation_service = ValidationService()
llm_fallback_extractor = LLMFallbackExtractor()
parsing_service = ParsingService(
    validation_service=validation_service,
    llm_fallback_extractor=llm_fallback_extractor,
)


@mcp.tool(name="parse_provider_content")
def parse_provider_content(
    provider_name: str,
    markdown: str = "",
    html: str = "",
) -> dict:
    raw_content = markdown.strip() if markdown.strip() else html.strip()

    if not raw_content:
        return {
            "success": False,
            "error": "No raw content provided.",
        }

    records = parsing_service.parse_document(
        provider_name=provider_name,
        raw_content=raw_content,
    )

    return {
        "success": True,
        "data": records,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")