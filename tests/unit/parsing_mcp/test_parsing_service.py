import pytest

from apps.parsing_mcp.services.parsing_service import ParsingService

pytestmark = pytest.mark.unit


def test_deterministic_parsing(parsing_service_no_llm: ParsingService):
    raw = "DeepSeek V3 0.27 / 1M input and 1.10 / 1M output"

    result = parsing_service_no_llm.parse_document("deepinfra", raw)

    assert len(result.records) == 1
    assert result.metadata.used_fallback is False


def test_llm_fallback(parsing_service_with_llm: ParsingService):
    raw = "random garbage"

    result = parsing_service_with_llm.parse_document("groq", raw)

    assert len(result.records) == 1
    assert result.metadata.used_fallback is True