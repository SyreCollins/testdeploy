import importlib
import logging

from app.core.config import Settings
from app.rag.vector_store.base import BaseVectorStore
from app.rag.vector_store.memory import MemoryVectorStore

logger = logging.getLogger("zam-ai-core-api.vector-store-factory")

PROVIDER_MAP: dict[str, str] = {
    "pinecone": "app.rag.vector_store.pinecone.PineconeVectorStore",
    "qdrant": "app.rag.vector_store.qdrant.QdrantVectorStore",
}


def _load_provider_class(name: str) -> type[BaseVectorStore]:
    module_path, class_name = PROVIDER_MAP[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_vector_store(settings: Settings) -> BaseVectorStore:
    store_name = (settings.vector_store or "").strip().lower()

    if store_name:
        if store_name not in PROVIDER_MAP:
            msg = f"Unknown vector store '{store_name}'. Supported: {list(PROVIDER_MAP.keys())}"
            raise ValueError(msg)
        return _instantiate(store_name, settings)

    auto_detect_order = ["pinecone", "qdrant"]
    for name in auto_detect_order:
        instance = _try_instantiate(name, settings)
        if instance is not None:
            return instance

    logger.warning("No vector store API key found — using MemoryVectorStore (data lost on restart)")
    return MemoryVectorStore()


def _try_instantiate(
    name: str,
    settings: Settings,
) -> BaseVectorStore | None:
    try:
        return _instantiate(name, settings)
    except (ValueError, KeyError, ImportError):
        return None


def _instantiate(
    name: str,
    settings: Settings,
) -> BaseVectorStore:
    cls = _load_provider_class(name)

    if name == "pinecone":
        api_key = settings.pinecone_api_key
        if not api_key:
            raise ValueError("ZAM_AI_PINECONE_API_KEY is not set")
        return cls(api_key=api_key, index_name=settings.pinecone_index_name)

    if name == "qdrant":
        url = settings.qdrant_url or "http://localhost:6333"
        return cls(
            url=url,
            api_key=settings.qdrant_api_key,
            collection_name=settings.qdrant_collection_name,
        )

    raise ValueError(f"Unsupported vector store: {name}")
