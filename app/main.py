import logging

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.retrieval import router as retrieval_router
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware.api_key import InternalApiKeyMiddleware
from app.core.middleware.request_id import RequestIdMiddleware
from app.rag.embeddings.mock import MockEmbeddingProvider
from app.rag.embeddings.voyage import VoyageEmbeddingProvider
from app.rag.registry import RagRegistry
from app.rag.service import RetrievalService
from app.rag.vector_store.memory import MemoryVectorStore
from app.rag.vector_store.pinecone import PineconeVectorStore


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title="Zam AI Core API",
        description="Internal medical AI API service for Zamda Health.",
        version=settings.service_version,
        docs_url="/docs" if settings.enable_openapi_docs else None,
        redoc_url="/redoc" if settings.enable_openapi_docs else None,
        openapi_url="/openapi.json" if settings.enable_openapi_docs else None,
    )

    app.state.settings = settings
    app.state.logger = logging.getLogger(settings.service_name)

    registry = RagRegistry(database_url=settings.database_url)
    registry.init_db()

    if settings.voyage_api_key:
        embedding_provider = VoyageEmbeddingProvider(
            api_key=settings.voyage_api_key,
            model=settings.voyage_embedding_model,
        )
        app.state.logger.info(f"Using Voyage embedding provider ({settings.voyage_embedding_model})")
    else:
        embedding_provider = MockEmbeddingProvider()
        app.state.logger.warning("No VOYAGE_API_KEY set — using MockEmbeddingProvider")

    if settings.pinecone_api_key:
        vector_store = PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            index_name=settings.pinecone_index_name,
        )
        app.state.logger.info(f"Using Pinecone vector store (index: {settings.pinecone_index_name})")
    else:
        vector_store = MemoryVectorStore()
        app.state.logger.warning("No PINECONE_API_KEY set — using MemoryVectorStore")

    app.state.retrieval_service = RetrievalService(
        registry=registry,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    register_exception_handlers(app)

    app.add_middleware(InternalApiKeyMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router, prefix="/v1", tags=["system"])
    app.include_router(retrieval_router, prefix="/v1", tags=["retrieval"])

    return app


app = create_app()
