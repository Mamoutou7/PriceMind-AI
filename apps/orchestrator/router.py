from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from scripts.test_storage_pipeline import provider_repository


class IntentType(StrEnum):
    PRICE_LOOKUP = "price_lookup"
    COMPARE_PROVIDERS = "compare_providers"
    SHOW_STORED_DATA = "show_stored_data"
    REFRESH_PROVIDER = "refresh_provider"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Intent:
    intent_type: IntentType
    user_query: str
    providers: list[str]
    model_name: str | None


class QueryRouter:
    """Detects user intent and extracts the main entities."""
    KNOWN_PROVIDERS = {
        "cloudrift",
        "deepinfra",
        "fireworks",
        "groq"
    }

    def route_query(self, user_query: str) -> Intent:
        normalized = user_query.strip().lower()

        if normalized in {"show data", "show stored data", "list data"}:
            return Intent(
                intent_type=IntentType.SHOW_STORED_DATA,
                user_query=user_query,
                providers=[],
                model_name=None,
            )

        if "compare" in normalized:
            return Intent(
                intent_type=IntentType.COMPARE_PROVIDERS,
                user_query=user_query,
                providers=self.extract_providers(normalized),
                model_name=self.extract_model_name(normalized),
            )


        if any(word in normalized for word in {"price", "cost", "pricing", "charge"}):
            return Intent(
                intent_type=IntentType.PRICE_LOOKUP,
                user_query=user_query,
                providers=self.extract_providers(normalized),
                model_name=self.extract_model_name(normalized),
            )

        return Intent(
            intent_type=IntentType.UNKNOWN,
            user_query=user_query,
            providers=[],
            model_name=None,
        )

    def extract_providers(self, query: str) -> list[str]:
        return [provider for provider in self.KNOWN_PROVIDERS if provider in query]

    @staticmethod
    def extract_model_name(query: str) -> str | None:
        match = re.match(r"for\s(.+)$", query)

        if not match:
            return None

        model_name = match.group(1).strip()
        return model_name or None