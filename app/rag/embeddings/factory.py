import importlib
import logging

from app.core.config import Settings
from app.rag.embeddings.base import BaseEmbeddingProvider
from app.rag.embeddings.mock import MockEmbeddingProvider

logger = logging.getLogger("zam-ai-core-api.embedding-factory")

PROVIDER_MAP: dict[str, str] = {
    "voyage": "app.rag.embeddings.voyage.VoyageEmbeddingProvider",
    "jina": "app.rag.embeddings.jina.JinaEmbeddingProvider",
    "gemini": "app.rag.embeddings.gemini.GeminiEmbeddingProvider",
}


def _load_provider_class(name: str) -> type[BaseEmbeddingProvider]:
    module_path, class_name = PROVIDER_MAP[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_embedding_provider(settings: Settings) -> BaseEmbeddingProvider:
    provider_name = (settings.embedding_provider or "").strip().lower()

    if provider_name:
        if provider_name not in PROVIDER_MAP:
            msg = f"Unknown embedding provider '{provider_name}'. Supported: {list(PROVIDER_MAP.keys())}"
            raise ValueError(msg)
        return _instantiate(provider_name, settings)

    auto_detect_order = ["jina", "voyage", "gemini"]
    for name in auto_detect_order:
        instance = _try_instantiate(name, settings)
        if instance is not None:
            return instance

    logger.warning("No embedding API key found — using MockEmbeddingProvider (not for production)")
    return MockEmbeddingProvider()


def _try_instantiate(
    name: str,
    settings: Settings,
) -> BaseEmbeddingProvider | None:
    try:
        return _instantiate(name, settings)
    except (ValueError, KeyError, ImportError):
        return None


def _instantiate(
    name: str,
    settings: Settings,
) -> BaseEmbeddingProvider:
    cls = _load_provider_class(name)

    if name == "voyage":
        api_key = settings.voyage_api_key
        if not api_key:
            raise ValueError("ZAM_AI_VOYAGE_API_KEY is not set")
        return cls(
            api_key=api_key,
            model=settings.voyage_embedding_model,
        )
    elif name == "jina":
        api_key = settings.jina_api_key
        if not api_key:
            raise ValueError("ZAM_AI_JINA_API_KEY is not set")
        return cls(api_key=api_key)
    elif name == "gemini":
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("ZAM_AI_GEMINI_API_KEY is not set")
        return cls(api_key=api_key)

    raise ValueError(f"Unsupported provider: {name}")
