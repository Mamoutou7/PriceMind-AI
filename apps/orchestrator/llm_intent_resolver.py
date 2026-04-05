from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from apps.orchestrator.router import Intent, IntentType
from core.providers import list_supported_providers
from core.settings import get_settings


@dataclass(frozen=True)
class LLMDecision:
    """High-level LLM decision for orchestration."""

    needs_tools: bool
    intent: Intent
    direct_answer: str | None = None


class LLMIntentResolver:
    """
    Uses an LLM to decide whether tools are needed and to extract a high-level intent.

    The LLM does not build a detailed execution plan.
    It only decides:
    - whether tools are needed
    - which business intent applies
    - which providers/model are relevant
    """

    def __init__(self, client: OpenAI | None = None) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for LLM orchestration.")

        self._client = client or OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
        self._model = settings.model_name or "gpt-4o-mini"

    def resolve(self, user_query: str) -> LLMDecision:
        prompt = self._build_prompt(user_query)

        response = self._client.responses.create(
            model=self._model,
            input=prompt,
        )

        raw_text = (response.output_text or "").strip()
        payload = self._parse_json_object(raw_text)

        needs_tools = bool(payload.get("needs_tools", False))
        intent_type = self._parse_intent_type(str(payload.get("intent_type", "unknown")))
        providers = self._normalize_providers(payload.get("providers", []))
        model_name = self._normalize_optional_string(payload.get("model_name"))
        direct_answer = self._normalize_optional_string(payload.get("direct_answer"))

        intent = Intent(
            intent_type=intent_type,
            user_query=user_query,
            providers=providers,
            model_name=model_name,
        )

        return LLMDecision(
            needs_tools=needs_tools,
            intent=intent,
            direct_answer=direct_answer,
        )

    def _build_prompt(self, user_query: str) -> str:
        supported_providers = list_supported_providers()

        return f"""
You are the intent resolution layer for PriceMind AI.

Your task:
1. Decide whether the user's request requires tools
2. Classify the request into one supported intent
3. Extract providers and model name when relevant

Supported intent types:
- price_lookup
- compare_providers
- show_stored_data
- refresh_provider
- unknown

Supported providers:
{json.dumps(supported_providers)}

Return ONLY valid JSON with this exact structure:

{{
  "needs_tools": true,
  "intent_type": "compare_providers",
  "providers": ["groq", "fireworks"],
  "model_name": "llama 3.3 70b",
  "direct_answer": null
}}

Rules:
- Use needs_tools=false only if the user can be answered without scraping/querying/stored data access
- For provider pricing lookups, comparisons, refreshes, or stored data queries, tools are usually needed
- providers must contain only supported providers
- model_name should be null if absent
- direct_answer should be null unless needs_tools is false
- never return markdown
- never return extra text outside JSON

User query:
{user_query}
""".strip()

    @staticmethod
    def _parse_json_object(text: str) -> dict[str, Any]:
        text = text.strip()

        fenced_match = re.match(
            r"^```(?:json)?\s*(.*?)\s*```$",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced_match:
            text = fenced_match.group(1).strip()

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end < start:
            raise ValueError(f"No JSON object found in LLM response: {text[:500]}")

        parsed = json.loads(text[start : end + 1])
        if not isinstance(parsed, dict):
            raise ValueError("LLM response must be a JSON object.")
        return parsed

    @staticmethod
    def _parse_intent_type(raw_value: str) -> IntentType:
        normalized = raw_value.strip().lower()
        mapping = {
            "price_lookup": IntentType.PRICE_LOOKUP,
            "compare_providers": IntentType.COMPARE_PROVIDERS,
            "show_stored_data": IntentType.SHOW_STORED_DATA,
            "refresh_provider": IntentType.REFRESH_PROVIDER,
            "unknown": IntentType.UNKNOWN,
        }
        return mapping.get(normalized, IntentType.UNKNOWN)

    @staticmethod
    def _normalize_optional_string(value: Any) -> str | None:
        if value is None:
            return None

        cleaned = str(value).strip()
        return cleaned if cleaned else None

    @staticmethod
    def _normalize_providers(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []

        supported = set(list_supported_providers())
        normalized: list[str] = []

        for item in value:
            provider = str(item).strip().lower()
            if provider in supported and provider not in normalized:
                normalized.append(provider)

        return normalized