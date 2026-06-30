from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ZAM_AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "local"
    service_name: str = "zam-ai-core-api"
    service_version: str = "0.1.0"
    log_level: str = "INFO"
    enable_openapi_docs: bool = True
    internal_api_keys: list[str] = Field(default_factory=list)
    readiness_check_dependencies: bool = False
    database_url: str = "sqlite:///./rag_registry.db"

    @property
    def is_local(self) -> bool:
        return self.environment.lower() in {"local", "dev", "development"}

    @field_validator("internal_api_keys", mode="before")
    @classmethod
    def parse_internal_api_keys(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [key.strip() for key in value.split(",") if key.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
