from __future__ import annotations

from pathlib import Path
from typing import Any

from core.config import RAW_DATA_DIR


def get_raw_provider_content_tool(
    provider_name: str,
    base_directory: Path | None = None,
) -> dict[str, Any]:
    root = base_directory or RAW_DATA_DIR
    provider_dir = root / provider_name.strip().lower()

    markdown_path = provider_dir / "page.markdown.txt"
    html_path = provider_dir / "page.html.txt"

    markdown = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
    html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""

    return {
        "success": bool(markdown or html),
        "provider_name": provider_name.strip().lower(),
        "markdown": markdown,
        "html": html,
    }