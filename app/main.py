import logging

from fastapi import FastAPI

from app.ai.audit import AuditTraceWriter
from app.ai.gateway import get_model_provider
from app.ai.orchestrator import ConversationOrchestrator
from app.ai.prompts import PromptManager
from app.api.keys.service import store as api_key_store
from app.api.routes.ai import router as ai_router
from app.api.routes.audit import router as audit_router
from app.api.routes.health import router as health_router
from app.api.routes.keys import router as keys_router
from app.api.routes.retrieval import router as retrieval_router
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware.api_key import InternalApiKeyMiddleware
from app.core.middleware.rate_limit import RateLimitMiddleware
from app.core.middleware.request_id import RequestIdMiddleware
from app.rag.embeddings import get_embedding_provider
from app.rag.registry import RagRegistry
from app.rag.service import RetrievalService
from app.rag.vector_store import get_vector_store


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

    if settings.internal_api_keys_list:
        api_key_store.bootstrap_static_keys(settings.internal_api_keys_list)

    registry = RagRegistry(database_url=settings.database_url)
    registry.init_db()

    embedding_provider = get_embedding_provider(settings)
    vector_store = get_vector_store(settings)

    app.state.logger.info(
        f"Using embedding provider: {type(embedding_provider).__name__}, "
        f"vector store: {type(vector_store).__name__}"
    )

    app.state.prompt_manager = PromptManager()
    app.state.audit_writer = AuditTraceWriter()

    app.state.retrieval_service = RetrievalService(
        registry=registry,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    try:
        model_provider = get_model_provider(settings)
        app.state.logger.info(
            f"Using model provider: {type(model_provider).__name__}"
        )
    except Exception:
        app.state.logger.warning("No model provider configured — will use per-request fallback")
        model_provider = None

    app.state.orchestrator = ConversationOrchestrator(
        retrieval_service=app.state.retrieval_service,
        prompt_manager=app.state.prompt_manager,
        model_provider=model_provider,
        settings=settings,
        audit_writer=app.state.audit_writer,
    )

    register_exception_handlers(app)

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(InternalApiKeyMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router, prefix="/v1", tags=["system"])
    app.include_router(retrieval_router, prefix="/v1", tags=["retrieval"])
    app.include_router(ai_router, prefix="/v1", tags=["ai"])
    app.include_router(keys_router, prefix="/v1/admin", tags=["admin"])
    app.include_router(audit_router, prefix="/v1", tags=["audit"])

    return app


if __name__ == "__main__":
    app = create_app()
