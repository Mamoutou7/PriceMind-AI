from __future__ import annotations

import json
import sys
from pathlib import Path

from apps.parsing_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parsing_mcp.services.parsing_service import ParsingService
from apps.parsing_mcp.services.validation_service import ValidationService


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python -m scripts.run_parser <provider_name> <path_to_raw_file>")
        raise SystemExit(1)

    provider_name = sys.argv[1]
    file_path = Path(sys.argv[2])

    raw_content = file_path.read_text(encoding="utf-8")

    service = ParsingService(
        validation_service=ValidationService(),
        llm_fallback_extractor=LLMFallbackExtractor(),
    )
    result = service.parse_document(provider_name=provider_name, raw_content=raw_content)

    print(
        json.dumps(
            {
                "records": [record.model_dump() for record in result.records],
                "metadata": result.metadata.model_dump(),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()