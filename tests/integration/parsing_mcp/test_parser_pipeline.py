from pathlib import Path

import pytest

from apps.parsing_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parsing_mcp.services.parsing_service import ParsingService
from apps.parsing_mcp.services.validation_service import ValidationService


@pytest.mark.integration
def test_parser_pipeline_on_fixture() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    markdown_path = base_dir / "data" / "raw" / "deepinfra" / "page.markdown.txt"

    raw_content = markdown_path.read_text(encoding="utf-8")

    validation_service = ValidationService()
    llm_fallback_extractor = LLMFallbackExtractor()
    parsing_service = ParsingService(
        validation_service=validation_service,
        llm_fallback_extractor=llm_fallback_extractor,
    )

    records = parsing_service.parse_document(
        provider_name="deepinfra",
        raw_content=raw_content,
    )

    assert len(records) >= 1
    assert records[0].provider_name == "deepinfra"
