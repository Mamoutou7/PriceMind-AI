from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

from apps.orchestrator.planner import ExecutionPlan

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes plan steps against registered MCP servers."""

    def __init__(self, servers_by_tool: Mapping[str, Any]) -> None:
        self._servers_by_tool = dict(servers_by_tool)

    async def execute(self, plan: ExecutionPlan) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        context: dict[str, Any] = {"providers": {}}

        for step in plan.steps:
            server = self._servers_by_tool.get(step.tool_name)
            if server is None:
                results.append(
                    {
                        "tool_name": step.tool_name,
                        "success": False,
                        "error": "No server registered for this tool.",
                    }
                )
                continue

            try:
                arguments = self._resolve_arguments(step.arguments, context)
                raw_result = await server.execute_tool(step.tool_name, arguments)
                normalized_result = self._normalize_tool_result(raw_result)

                self._update_context(arguments, step.tool_name, normalized_result, context)

                results.append(
                    {
                        "tool_name": step.tool_name,
                        "success": True,
                        "data": normalized_result,
                    }
                )
            except Exception as exc:
                logger.exception("Tool '%s' execution failed.", step.tool_name)
                results.append(
                    {
                        "tool_name": step.tool_name,
                        "success": False,
                        "error": str(exc),
                    }
                )

        return results

    def _resolve_arguments(
        self,
        arguments: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        resolved = dict(arguments)
        source = resolved.pop("__from_previous__", None)
        provider_name = resolved.pop("__provider__", None)
        provider_context = context.get("providers", {}).get(provider_name, {})

        if source == "raw_content":
            raw_content = provider_context.get("raw_content", {})
            resolved["markdown"] = raw_content.get("markdown", "")
            resolved["html"] = raw_content.get("html", "")

        elif source == "parsed_prices":
            resolved["records"] = provider_context.get("parsed_prices", [])

        return resolved

    @staticmethod
    def _normalize_tool_result(raw_result: Any) -> Any:
        if hasattr(raw_result, "content"):
            text_parts: list[str] = []

            for item in raw_result.content:
                item_text = getattr(item, "text", None)
                if item_text:
                    text_parts.append(item_text)

            if text_parts:
                joined_text = "\n".join(text_parts).strip()
                try:
                    return json.loads(joined_text)
                except json.JSONDecodeError:
                    return joined_text

        return raw_result

    @staticmethod
    def _update_context(
        arguments: dict[str, Any],
        tool_name: str,
        normalized_result: Any,
        context: dict[str, Any],
    ) -> None:
        if not isinstance(normalized_result, dict):
            return

        provider_name = str(arguments.get("provider_name", "")).strip().lower()
        if not provider_name:
            return

        providers_context = context.setdefault("providers", {})
        provider_context = providers_context.setdefault(provider_name, {})

        if tool_name == "get_raw_provider_content" and normalized_result.get("success"):
            provider_context["raw_content"] = normalized_result

        if tool_name == "parse_provider_content" and normalized_result.get("success"):
            parsed_payload = normalized_result.get("data", {})
            if isinstance(parsed_payload, dict):
                provider_context["parsed_prices"] = parsed_payload.get("records", [])