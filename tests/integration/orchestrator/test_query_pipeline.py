from __future__ import annotations

import pytest

from apps.orchestrator.executor import ToolExecutor
from apps.orchestrator.planner import QueryPlanner
from apps.orchestrator.router import IntentType, QueryRouter


class FakeServer:
    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name

    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        if tool_name == "scrape_provider":
            return {"success": True, "provider_name": arguments["provider_name"]}
        if tool_name == "get_raw_provider_content":
            return {
                "success": True,
                "provider_name": arguments["provider_name"],
                "markdown": "| Model | Input | Output |\n|---|---:|---:|\n| llama 3.3 70b | 0.59 | 0.79 |",
                "html": "",
            }
        if tool_name == "parse_provider_content":
            return {
                "success": True,
                "data": {
                    "records": [
                        {
                            "provider_name": arguments["provider_name"],
                            "model_name": "llama 3.3 70b",
                            "input_price_per_1m": 0.59,
                            "output_price_per_1m": 0.79,
                            "currency": "USD",
                        }
                    ]
                },
            }
        if tool_name == "store_parsed_prices":
            return {"success": True, "inserted_count": len(arguments.get("records", []))}
        if tool_name == "compare_prices":
            return {
                "success": True,
                "data": [
                    {
                        "provider_name": "groq",
                        "model_name": "llama 3.3 70b",
                        "input_price_per_1m": 0.59,
                        "output_price_per_1m": 0.79,
                        "currency": "USD",
                    }
                ],
            }
        raise AssertionError(f"Unexpected tool call: {tool_name}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_pipeline_end_to_end_fake_servers() -> None:
    router = QueryRouter()
    intent = router.route_query("price of llama 3.3 70b on groq")
    assert intent.intent_type == IntentType.PRICE_LOOKUP

    planner = QueryPlanner()
    plan = planner.build_plan(intent)
    assert plan.steps

    fake_server = FakeServer("all")
    executor = ToolExecutor(
        {
            "scrape_provider": fake_server,
            "get_raw_provider_content": fake_server,
            "parse_provider_content": fake_server,
            "store_parsed_prices": fake_server,
            "compare_prices": fake_server,
        }
    )

    results = await executor.execute(plan)

    assert any(result["tool_name"] == "compare_prices" for result in results)
    assert all(result["success"] is True for result in results)