from pathlib import Path

from apps.parser_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from apps.parser_mcp.services.parsing_service import ParsingService
from apps.parser_mcp.services.validation_service import ValidationService

BASE_DIR = Path(__file__).resolve().parents[1]
MARKDOWN_PATH = BASE_DIR / "data" / "raw" / "deepinfra" / "page.markdown.txt"

raw_content = MARKDOWN_PATH.read_text(encoding="utf-8")

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

print("PARSED RECORD COUNT:", len(records))
for record in records[:5]:
    print(record)