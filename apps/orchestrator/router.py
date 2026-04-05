from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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