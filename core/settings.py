from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="", alias="OPENAI_BASE_URL")
    model_name: str = Field(default="", alias="MODEL_NAME")
    firecrawl_api_key: str = Field(default="", alias="FIRECRAWL_API_KEY")

    @property
    def llm_fallback_enabled(self) -> bool:
        return bool(self.openai_api_key and self.openai_base_url and self.model_name)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()