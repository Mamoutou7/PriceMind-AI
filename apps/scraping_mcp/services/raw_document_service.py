from __future__ import annotations

from pathlib import Path

from core.config import RAW_DATA_DIR


class RawDocumentService:
    """Persists raw scraped documents on disk."""

    def __init__(self, base_directory: Path | None = None) -> None:
        self._base_directory = base_directory or RAW_DATA_DIR

    def save(self, provider_name: str, format_name: str, content: str) -> str:
        provider_directory = self._base_directory / provider_name
        provider_directory.mkdir(parents=True, exist_ok=True)

        file_path = provider_directory / f"page.{format_name}.txt"
        file_path.write_text(content, encoding="utf-8")

        return str(file_path)
