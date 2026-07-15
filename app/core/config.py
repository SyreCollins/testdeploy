from functools import lru_cache

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
    internal_api_keys: str = ""
    readiness_check_dependencies: bool = False
    database_url: str = "sqlite:///./rag_registry.db"
    embedding_provider: str = ""
    voyage_api_key: str | None = None
    voyage_embedding_model: str = "voyage-3"
    jina_api_key: str | None = None
    gemini_api_key: str | None = None

    embedding_batch_timeout: int = 180

    model_timeout: int = 60
    model_retry_count: int = 1

    model_provider: str = ""
    claude_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-6"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    vector_store: str = ""
    pinecone_api_key: str | None = None
    pinecone_index_name: str = "zam-ai"
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_collection_name: str = "zam-ai"

    @property
    def internal_api_keys_list(self) -> list[str]:
        if not self.internal_api_keys:
            return []
        return [k.strip() for k in self.internal_api_keys.split(",") if k.strip()]

    @property
    def is_local(self) -> bool:
        return self.environment.lower() in {"local", "dev", "development"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
