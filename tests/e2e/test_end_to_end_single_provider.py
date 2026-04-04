from __future__ import annotations

import pytest

from apps.parsing_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parsing_mcp.services.parsing_service import ParsingService
from apps.parsing_mcp.services.validation_service import ValidationService


@pytest.mark.e2e
def test_end_to_end_single_provider() -> None:
    raw_content = """
    | Model | Input | Output |
    |---|---:|---:|
    | llama 3.3 70b | 0.59 | 0.79 |
    """

    service = ParsingService(
        validation_service=ValidationService(),
        llm_fallback_extractor=LLMFallbackExtractor(),
    )
    result = service.parse_document("groq", raw_content)

    assert len(result.records) == 1
    assert result.records[0].provider_name == "groq"
    assert result.records[0].model_name == "llama 3.3 70b"