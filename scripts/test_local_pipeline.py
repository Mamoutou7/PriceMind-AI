from __future__ import annotations

from pathlib import Path

from apps.parsing_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parsing_mcp.services.parsing_service import ParsingService
from apps.parsing_mcp.services.validation_service import ValidationService


def main() -> None:
    path = Path("tests/integration/data/raw/deepinfra/page.markdown.txt")
    raw_content = path.read_text(encoding="utf-8")

    service = ParsingService(
        validation_service=ValidationService(),
        llm_fallback_extractor=LLMFallbackExtractor(),
    )
    result = service.parse_document("deepinfra", raw_content)

    print("Parsed records:", len(result.records))
    for record in result.records[:5]:
        print(record.model_dump())


if __name__ == "__main__":
    main()