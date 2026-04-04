from __future__ import annotations

from core.config import PROVIDER_URLS


def get_provider_url(provider_name: str) -> str:
    normalized = provider_name.strip().lower()
    try:
        return PROVIDER_URLS[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown provider: {provider_name}") from exc


def list_supported_providers() -> list[str]:
    return sorted(PROVIDER_URLS.keys())