import logging

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.ai.audit import AuditTraceWriter
from app.ai.gateway import get_model_provider
from app.ai.orchestrator import ConversationOrchestrator
from app.ai.prompts import PromptManager
from app.api.keys.service import store as api_key_store
from app.db.engine import init_db as init_platform_db
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
from app.core.middleware.request_logger import RequestLoggingMiddleware
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
        swagger_ui_parameters={"persistAuthorization": True},
    )

    app.state.settings = settings
    app.state.logger = logging.getLogger(settings.service_name)

    db_engine = init_platform_db(settings.database_url)
    api_key_store._engine = db_engine

    if settings.internal_api_keys_list:
        api_key_store.bootstrap_static_keys(settings.internal_api_keys_list)

    app.state.logger.info(
        "app_starting",
        extra={
            "environment": settings.environment,
            "embedding_provider": settings.embedding_provider or "auto-detect",
            "vector_store": settings.vector_store or "auto-detect",
            "model_provider": settings.model_provider or "auto-detect",
            "database_url": settings.database_url,
            "has_pinecone_key": bool(settings.pinecone_api_key),
            "has_jina_key": bool(settings.jina_api_key),
            "has_claude_key": bool(settings.claude_api_key),
            "has_voyage_key": bool(settings.voyage_api_key),
        },
    )

    app.state.logger.info(f"Platform DB initialized at: {settings.database_url}")
    app.state.db_engine = db_engine

    registry = RagRegistry(database_url=settings.database_url)
    registry.init_db()

    embedding_provider = get_embedding_provider(settings)
    vector_store = get_vector_store(settings)

    app.state.logger.info(
        f"Using embedding provider: {type(embedding_provider).__name__}, "
        f"vector store: {type(vector_store).__name__}"
    )

    app.state.prompt_manager = PromptManager()
    app.state.audit_writer = AuditTraceWriter(database_url=settings.database_url)

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
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(health_router, prefix="/v1", tags=["system"])
    app.include_router(retrieval_router, prefix="/v1", tags=["retrieval"])
    app.include_router(ai_router, prefix="/v1", tags=["ai"])
    app.include_router(keys_router, prefix="/v1/admin", tags=["admin"])
    app.include_router(audit_router, prefix="/v1", tags=["audit"])

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})
        schema["components"]["securitySchemes"]["ApiKeyAuth"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-Zam-AI-Key",
        }
        schema["security"] = [{"ApiKeyAuth": []}]
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi

    return app


if __name__ == "__main__":
    app = create_app()
