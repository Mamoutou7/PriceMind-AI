from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "pricing.sqlite"
CONFIG_PATH = BASE_DIR / "server_config.json"

PROVIDER_URLS = {
    "cloudrift": "https://www.cloudrift.ai/pricing",
    "deepinfra": "https://deepinfra.com/pricing",
    "fireworks": "https://fireworks.ai/pricing",
    "groq": "https://groq.com/pricing",
    "openai": "https://openai.com/pricing",
    "anthropic": "https://www.anthropic.com/pricing",
}

ALLOWED_PROVIDERS = {
    "cloudrift",
    "deepinfra",
    "fireworks",
    "groq",
}

KNOWN_PROVIDERS = ("cloudrift", "deepinfra", "fireworks", "groq")
