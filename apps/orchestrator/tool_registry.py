from __future__ import annotations

from typing import Any


def get_tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "get_latest_prices",
            "description": (
                "Returns the latest stored pricing records from the SQLite "
                "database."
            ),
            "arguments_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer"}},
                "required": [],
            },
        },
        {
            "name": "compare_prices",
            "description": "Compares stored prices across providers for one model.",
            "arguments_schema": {
                "type": "object",
                "properties": {
                    "providers": {"type": "array", "items": {"type": "string"}},
                    "model_name": {"type": "string"},
                },
                "required": ["providers", "model_name"],
            },
        },
        {
            "name": "scrape_provider",
            "description": (
                "Loads previously saved raw markdown/html content for a provider."
            ),
            "arguments_schema": {
                "type": "object",
                "properties": {
                    "provider_name": {"type": "string"},
                    "url": {"type": "string"},
                    "formats": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["provider_name", "url"],
            },
        },
        {
            "name": "get_raw_provider_content",
            "description": (
                "Loads previously saved raw markdown/html content for a provider."
            ),
            "arguments_schema": {
                "type": "object",
                "properties": {"provider_name": {"type": "string"}},
                "required": ["provider_name"],
            },
        },
        {
            "name": "parse_provider_content",
            "description": (
                "Parses markdown/html pricing content into structured pricing "
                "records."
            ),
            "arguments_schema": {
                "type": "object",
                "properties": {
                    "provider_name": {"type": "string"},
                    "markdown": {"type": "string"},
                    "html": {"type": "string"},
                },
                "required": ["provider_name"],
            },
        },
        {
            "name": "store_parsed_prices",
            "description": "Stores parsed pricing records into SQLite.",
            "arguments_schema": {
                "type": "object",
                "properties": {
                    "records": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["records"],
            },
        },
    ]
