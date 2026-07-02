import hmac

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import Settings
from app.core.request_context import get_request_id


class InternalApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    _PUBLIC_PATHS = {"/v1/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self._PUBLIC_PATHS:
            return await call_next(request)

        if not self.settings.internal_api_keys_list:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "request_id": get_request_id(request),
                    "status": "error",
                    "error": {
                        "code": "internal_api_key_not_configured",
                        "message": "Internal API key authentication is not configured.",
                        "retryable": False,
                        "details": {},
                    },
                },
            )

        provided_key = request.headers.get("x-zam-ai-key")
        if not provided_key or not self._is_valid_key(provided_key):
            request.app.state.logger.warning(
                "internal_api_auth_failed",
                extra={
                    "request_id": get_request_id(request),
                    "path": request.url.path,
                    "caller_service": request.headers.get("x-caller-service"),
                },
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "request_id": get_request_id(request),
                    "status": "error",
                    "error": {
                        "code": "authentication_failed",
                        "message": "Invalid or missing internal API key.",
                        "retryable": False,
                        "details": {},
                    },
                },
            )

        return await call_next(request)

    def _is_valid_key(self, provided_key: str) -> bool:
        return any(
            hmac.compare_digest(provided_key, expected_key)
            for expected_key in self.settings.internal_api_keys_list
        )

