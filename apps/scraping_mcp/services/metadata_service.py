from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.config import RAW_DATA_DIR


class MetadataService:
    """Manages scrape metadata persisted in a JSON file."""

    def __init__(self, metadata_path: Path | None = None) -> None:
        self._metadata_path = metadata_path or (RAW_DATA_DIR / "scraped_metadata.json")
        self._metadata_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self._metadata_path.exists():
            return {}

        raw = json.loads(self._metadata_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Scrape metadata file must contain a JSON object.")

        return raw

    def save(self, metadata: dict[str, Any]) -> None:
        self._metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )