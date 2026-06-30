import logging

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware.api_key import InternalApiKeyMiddleware
from app.core.middleware.request_id import RequestIdMiddleware


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

    register_exception_handlers(app)

    app.add_middleware(InternalApiKeyMiddleware, settings=settings)
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router, prefix="/v1", tags=["system"])

    return app


app = create_app()
