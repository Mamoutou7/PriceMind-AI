from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MetadataService:
    """Reads and writes scraped metadata."""

    def __init__(self, metadata_path: Path) -> None:
        self.metadata_path = metadata_path

    def load(self) -> dict[str, Any]:
        if not self.metadata_path.exists():
            return {}

        with self.metadata_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    def save(self, metadata: dict[str, Any]) -> None:
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with self.metadata_path.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=2, ensure_ascii=False)
