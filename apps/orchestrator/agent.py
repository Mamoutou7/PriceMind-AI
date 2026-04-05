from __future__ import annotations

from typing import Any

from apps.orchestrator.executor import ToolExecutor
from apps.orchestrator.llm_client import LLMClient
from apps.orchestrator.tool_registry import get_tool_definitions
from core.providers import get_provider_url, list_supported_providers


class AgentOrchestrator:
    """LLM-driven orchestration loop."""

    def __init__(self, executor: ToolExecutor, llm_client: LLMClient) -> None:
        self._executor = executor
        self._llm_client = llm_client

    async def run(self, user_query: str, max_steps: int = 8) -> dict[str, Any]:
        tool_history: list[dict[str, Any]] = []
        tools = get_tool_definitions()

        for _ in range(max_steps):
            decision = self._llm_client.decide_next_action(
                user_query=user_query,
                tools=tools,
                tool_history=tool_history,
            )

            action = decision.get("action")

            if action == "final_response":
                return {
                    "success": True,
                    "answer": str(decision.get("answer", "")).strip(),
                    "tool_history": tool_history,
                }

            if action != "tool_call":
                return {
                    "success": False,
                    "error": f"Unknown action returned by LLM: {action}",
                    "tool_history": tool_history,
                }

            tool_name = str(decision.get("tool_name", "")).strip()
            arguments = decision.get("arguments", {})
            if not isinstance(arguments, dict):
                return {
                    "success": False,
                    "error": "LLM returned invalid tool arguments.",
                    "tool_history": tool_history,
                }

            arguments = self._postprocess_tool_arguments(tool_name, arguments)

            result = await self._executor.execute_single(tool_name, arguments)

            tool_history.append(
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "result": result,
                }
            )

        return {
            "success": False,
            "error": "Max agent steps reached without final response.",
            "tool_history": tool_history,
        }

    @staticmethod
    def _postprocess_tool_arguments(
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        processed = dict(arguments)

        if tool_name == "scrape_provider":
            provider_name = str(processed.get("provider_name", "")).strip().lower()
            if provider_name and "url" not in processed:
                if provider_name in list_supported_providers():
                    processed["url"] = get_provider_url(provider_name)

        return processed
