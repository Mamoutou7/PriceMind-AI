from __future__ import annotations


class ValidationService:
    """Validates scrape inputs."""

    @staticmethod
    def validate_provider_name(provider_name: str) -> str:
        normalized = provider_name.strip().lower()
        if not normalized:
            raise ValueError("provider_name is required.")
        return normalized

    @staticmethod
    def validate_url(url: str) -> str:
        cleaned = url.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("url must start with http:// or https://")
        return cleaned
