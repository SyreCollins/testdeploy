from fastapi import APIRouter, Request

from app.api.schemas.health import DependencyStatus, HealthResponse, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        version=settings.service_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def ready(request: Request) -> ReadinessResponse:
    settings = request.app.state.settings

    dependencies = {
        "api": DependencyStatus(status="ok"),
    }

    if settings.readiness_check_dependencies:
        dependencies.update(
            {
                "metadata_store": DependencyStatus(status="not_configured"),
                "vector_store": DependencyStatus(status="not_configured"),
                "redis": DependencyStatus(status="not_configured"),
                "model_gateway": DependencyStatus(status="not_configured"),
            }
        )

    return ReadinessResponse(status="ready", dependencies=dependencies)

