from __future__ import annotations

import json
from pathlib import Path


class RawDocumentService:
    """Stores raw scraped documents on disk."""

    def __init__(self, base_directory: Path) -> None:
        self.base_directory = base_directory
        self.base_directory.mkdir(parents=True, exist_ok=True)

    def save(self, provider_name: str, format_name: str, content: str | dict) -> str:
        provider_dir = self.base_directory / provider_name.lower()
        provider_dir.mkdir(parents=True, exist_ok=True)

        file_path = provider_dir / f"page.{format_name}.txt"
        with file_path.open("w", encoding="utf-8") as file:
            if isinstance(content, str):
                file.write(content)
            else:
                file.write(json.dumps(content, indent=2, ensure_ascii=False))

        return str(file_path)
