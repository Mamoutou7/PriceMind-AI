from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from apps.orchestrator.agent_session import AgentChatSession
from apps.orchestrator.executor import ToolExecutor
from apps.orchestrator.llm_intent_resolver import LLMIntentResolver
from apps.orchestrator.planner import QueryPlanner
from apps.orchestrator.response_builder import ResponseBuilder
from core.config import CONFIG_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServerClient:
    """Thin wrapper over an initialized MCP client session."""

    def __init__(self, name: str, session: ClientSession) -> None:
        self.name = name
        self._session = session

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        return await self._session.call_tool(name=tool_name, arguments=arguments)


@asynccontextmanager
async def create_mcp_server_client(
    name: str,
    config: dict[str, Any],
) -> AsyncIterator[MCPServerClient]:
    server_params = StdioServerParameters(
        command=config["command"],
        args=config["args"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield MCPServerClient(name=name, session=session)


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        raw_data: object = json.load(file)

    if not isinstance(raw_data, dict):
        raise ValueError("server_config.json must contain a top-level JSON object.")

    config = cast(dict[str, Any], raw_data)
    mcp_servers = config.get("mcpServers", {})
    if "parsing_mcp" not in mcp_servers and "parser_mcp" in mcp_servers:
        mcp_servers["parsing_mcp"] = mcp_servers.pop("parser_mcp")
    config["mcpServers"] = mcp_servers
    return config


async def async_main() -> None:
    config = load_config()
    mcp_servers = config["mcpServers"]

    async with (
        create_mcp_server_client(
            name="scraping_mcp",
            config=mcp_servers["scraping_mcp"],
        ) as scraping_server,
        create_mcp_server_client(
            name="parsing_mcp",
            config=mcp_servers["parsing_mcp"],
        ) as parser_server,
        create_mcp_server_client(
            name="storage_mcp",
            config=mcp_servers["storage_mcp"],
        ) as storage_server,
    ):
        executor = ToolExecutor(
            {
                "scrape_provider": scraping_server,
                "scrape_all_providers": scraping_server,
                "get_scrape_result": scraping_server,
                "get_raw_provider_content": scraping_server,
                "parse_provider_content": parser_server,
                "get_latest_prices": storage_server,
                "upsert_provider_price": storage_server,
                "store_parsed_prices": storage_server,
                "compare_prices": storage_server,
            }
        )

        session = AgentChatSession(
            resolver=LLMIntentResolver(),
            planner=QueryPlanner(),
            executor=executor,
            response_builder=ResponseBuilder(),
        )
        await session.run()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()