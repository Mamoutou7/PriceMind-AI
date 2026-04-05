from __future__ import annotations

import pytest

from apps.orchestrator.llm_intent_resolver import LLMIntentResolver
from apps.orchestrator.router import IntentType


class FakeResponse:
    def __init__(self, output_text: str) -> None:
        self.output_text = output_text


class FakeResponsesAPI:
    def __init__(self, output_text: str) -> None:
        self._output_text = output_text

    def create(self, model: str, input: str) -> FakeResponse:
        return FakeResponse(self._output_text)


class FakeClient:
    def __init__(self, output_text: str) -> None:
        self.responses = FakeResponsesAPI(output_text)


@pytest.mark.unit
def test_resolver_returns_compare_intent(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o-mini")

    resolver = LLMIntentResolver(
        client=FakeClient(
            """
            {
              "needs_tools": true,
              "intent_type": "compare_providers",
              "providers": ["groq", "fireworks"],
              "model_name": "llama 3.3 70b",
              "direct_answer": null
            }
            """
        )
    )

    decision = resolver.resolve("compare groq and fireworks for llama 3.3 70b")

    assert decision.needs_tools is True
    assert decision.intent.intent_type == IntentType.COMPARE_PROVIDERS
    assert decision.intent.providers == ["groq", "fireworks"]
    assert decision.intent.model_name == "llama 3.3 70b"


@pytest.mark.unit
def test_resolver_returns_direct_answer(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o-mini")

    resolver = LLMIntentResolver(
        client=FakeClient(
            """
            {
              "needs_tools": false,
              "intent_type": "unknown",
              "providers": [],
              "model_name": null,
              "direct_answer": "Hello! I can explain how PriceMind works."
            }
            """
        )
    )

    decision = resolver.resolve("Explain how PriceMind works")

    assert decision.needs_tools is False
    assert decision.direct_answer == "Hello! I can explain how PriceMind works."