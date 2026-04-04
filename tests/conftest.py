from __future__ import annotations

import pytest

from apps.parsing_mcp.models.pricing import ParsedPricingRecord
from apps.parsing_mcp.services.parsing_service import ParsingService
from apps.parsing_mcp.services.validation_service import ValidationService
from core.settings import get_settings


class DummyLLMFallbackExtractor:
    def __init__(self, available: bool = False, records=None):
        self._available = available
        self._records = records or []
        self.calls = []

    def is_available(self) -> bool:
        return self._available

    def extract(self, provider_name: str, raw_content: str):
        self.calls.append((provider_name, raw_content))
        return self._records


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def validation_service():
    return ValidationService()


@pytest.fixture
def llm_disabled():
    return DummyLLMFallbackExtractor(False, [])


@pytest.fixture
def llm_enabled():
    return DummyLLMFallbackExtractor(
        True,
        [
            ParsedPricingRecord(
                provider_name="groq",
                model_name="llama-3.3-70b",
                input_price_per_1m="0.5",
                output_price_per_1m="0.8",
                currency="USD",
                extraction_method="llm",
                confidence=0.6,
            )
        ],
    )


@pytest.fixture
def parsing_service_no_llm(validation_service, llm_disabled):
    return ParsingService(validation_service, llm_disabled)


@pytest.fixture
def parsing_service_with_llm(validation_service, llm_enabled):
    return ParsingService(validation_service, llm_enabled)