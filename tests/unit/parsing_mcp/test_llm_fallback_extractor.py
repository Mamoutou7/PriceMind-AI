import pytest

from apps.parsing_mcp.services.llm_fallback_extractor import LLMFallbackExtractor
from core.settings import get_settings

pytestmark = pytest.mark.unit


def test_extract_json_array_from_raw_json() -> None:
    text = '[{"provider_name":"groq","model_name":"llama-3.3-70b"}]'

    result = LLMFallbackExtractor._extract_json_array(text)

    assert result == text


def test_extract_json_array_from_fenced_block() -> None:
    text = """
    ```json
    [{"provider_name":"groq","model_name":"llama-3.3-70b"}]
    ```
    """

    result = LLMFallbackExtractor._extract_json_array(text)

    assert result == '[{"provider_name":"groq","model_name":"llama-3.3-70b"}]'


def test_extract_json_array_from_text_with_prefix_and_suffix() -> None:
    text = """
    Here is the extracted data:
    [{"provider_name":"groq","model_name":"llama-3.3-70b"}]
    End of response.
    """

    result = LLMFallbackExtractor._extract_json_array(text)

    assert result == '[{"provider_name":"groq","model_name":"llama-3.3-70b"}]'


def test_is_available_returns_true_when_env_is_present(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("MODEL_NAME", "gpt-4o-mini")

    get_settings.cache_clear()

    extractor = LLMFallbackExtractor()

    assert extractor.is_available() is True