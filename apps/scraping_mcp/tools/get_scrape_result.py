from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_scrape_result_tool(metadata_path: Path, provider_name: str) -> dict[str, Any]:
    if not metadata_path.exists():
        return {"success": False, "error": "No metadata file found."}

    with metadata_path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if provider_name not in metadata:
        return {
            "success": False,
            "error": f"No scrape result found for '{provider_name}'.",
        }

    return {"success": True, "data": metadata[provider_name]}
