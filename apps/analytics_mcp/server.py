from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from apps.analytics_mcp.comparison_service import ComparisonService

mcp = FastMCP("analytics_mcp")
service = ComparisonService()


@mcp.tool(name="summarize_price_comparison")
def summarize_price_comparison(rows: list[dict]) -> dict:
    return service.summarize(rows)


if __name__ == "__main__":
    mcp.run(transport="stdio")
