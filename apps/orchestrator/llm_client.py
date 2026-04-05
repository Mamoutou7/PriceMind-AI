from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from core.settings import get_settings


class LLMClient:
    """Small wrapper around OpenAI responses API for orchestration decisions."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for LLM orchestration.")

        self._client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
        self._model = settings.model_name or "gpt-4o-mini"

    def decide_next_action(
        self,
        user_query: str,
        tools: list[dict[str, Any]],
        tool_history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        prompt = self._build_prompt(user_query, tools, tool_history)

        response = self._client.responses.create(
            model=self._model,
            input=prompt,
        )

        raw_text = (response.output_text or "").strip()

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM returned invalid JSON: {raw_text}") from exc

    @staticmethod
    def _build_prompt(
        user_query: str,
        tools: list[dict[str, Any]],
        tool_history: list[dict[str, Any]],
    ) -> str:
        return f"""
You are the orchestration brain of PriceMind AI.

Your job:
- decide whether a tool is needed
- choose the best tool if needed
- provide valid JSON only

Available tools:
{json.dumps(tools, indent=2)}

Previous tool history:
{json.dumps(tool_history, indent=2)}

User query:
{user_query}

You must return ONLY one JSON object with one of these shapes:

1) Tool call:
{{
  "action": "tool_call",
  "tool_name": "<tool name>",
  "arguments": {{}}
}}

2) Final response:
{{
  "action": "final_response",
  "answer": "<answer>"
}}

Rules:
- Use a tool only if fresh, stored, scraped, or computed data is needed.
- If the user asks to compare provider prices, tools are usually needed.
- If the user asks a general explanation, tools may not be needed.
- Never return markdown.
- Never return extra text outside JSON.
""".strip()
