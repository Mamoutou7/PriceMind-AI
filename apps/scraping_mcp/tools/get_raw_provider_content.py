from __future__ import annotations

from pathlib import Path
from typing import Any


def get_raw_provider_content_tool(
    provider_name: str,
    base_directory: Path,
) -> dict[str, Any]:
    provider_dir = base_directory / provider_name.lower()
    markdown_path = provider_dir / "page.markdown.txt"
    html_path = provider_dir / "page.html.txt"

    markdown = ""
    html = ""

    if markdown_path.exists():
        markdown = markdown_path.read_text(encoding="utf-8")

    if html_path.exists():
        html = html_path.read_text(encoding="utf-8")

    if not markdown and not html:
        return {
            "success": False,
            "error": f"No raw content found for provider '{provider_name}'.",
        }

    return {
        "success": True,
        "provider_name": provider_name.lower(),
        "markdown": markdown,
        "html": html,
    }