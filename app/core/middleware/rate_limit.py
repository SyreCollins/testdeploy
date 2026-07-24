from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.request_context import get_request_id

WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in {"/v1/health", "/docs", "/redoc", "/openapi.json"}:
            return await call_next(request)

        api_key_entry = getattr(request.state, "api_key_entry", None)
        if api_key_entry is None:
            return await call_next(request)

        key_id = api_key_entry["id"]
        org_plan = api_key_entry.get("org_plan", "free")
        settings = request.app.state.settings
        max_requests = settings.get_plan_rate_limit(org_plan)

        from app.api.keys.service import store as api_key_store

        allowed = api_key_store.check_rate_limit(
            key_id=key_id,
            max_requests=max_requests,
            window_seconds=WINDOW_SECONDS,
        )
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "request_id": get_request_id(request),
                    "status": "error",
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": f"Rate limit of {max_requests} requests per {WINDOW_SECONDS}s exceeded.",
                        "retryable": True,
                        "details": {},
                    },
                },
            )

        return await call_next(request)