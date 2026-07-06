import logging

from app.ai.gateway.base import BaseModelProvider
from app.ai.gateway.mock import MockModelProvider
from app.core.config import Settings

logger = logging.getLogger("zam-ai-core-api.model-gateway-factory")

PROVIDER_MAP: dict[str, str] = {
    "claude": "app.ai.gateway.claude.ClaudeProvider",
    "gemini": "app.ai.gateway.gemini.GeminiProvider",
}

AUTO_DETECT_ORDER = ["claude", "gemini"]


def _import_provider_class(name: str) -> type[BaseModelProvider]:
    import importlib

    module_path, class_name = PROVIDER_MAP[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_model_provider(settings: Settings) -> BaseModelProvider:
    provider_name = (settings.model_provider or "").strip().lower()

    if provider_name:
        if provider_name not in PROVIDER_MAP:
            msg = f"Unknown model provider '{provider_name}'. Supported: {list(PROVIDER_MAP.keys())}"
            raise ValueError(msg)
        return _instantiate(provider_name, settings)

    for name in AUTO_DETECT_ORDER:
        instance = _try_instantiate(name, settings)
        if instance is not None:
            return instance

    logger.warning("No model API key found — using MockModelProvider (not for production)")
    return MockModelProvider()


def _try_instantiate(name: str, settings: Settings) -> BaseModelProvider | None:
    try:
        return _instantiate(name, settings)
    except (ValueError, KeyError, ImportError):
        return None


def _instantiate(name: str, settings: Settings) -> BaseModelProvider:
    cls = _import_provider_class(name)

    if name == "claude":
        api_key = settings.claude_api_key
        if not api_key:
            raise ValueError("ZAM_AI_CLAUDE_API_KEY is not set")
        return cls(
            api_key=api_key,
            model=settings.claude_model,
        )
    elif name == "gemini":
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("ZAM_AI_GEMINI_API_KEY is not set")
        return cls(
            api_key=api_key,
            model=settings.gemini_model,
        )

    raise ValueError(f"Unsupported provider: {name}")
