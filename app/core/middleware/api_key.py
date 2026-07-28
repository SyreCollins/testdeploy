from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.api.keys.service import store as api_key_store
from app.core.config import Settings
from app.core.request_context import get_request_id


class InternalApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    _PUBLIC_PATHS = {
        "/v1/health", "/docs", "/redoc", "/openapi.json",
        "/v1/auth/webhook",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self._PUBLIC_PATHS:
            return await call_next(request)

        provided_key = request.headers.get("x-zam-ai-key")

        if not provided_key:
            clerk_id = getattr(request.state, "clerk_user_id", None)
            if clerk_id:
                return await call_next(request)
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

        entry = api_key_store.validate_key(provided_key)
        if entry is None:
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

        request.state.api_key_entry = entry
        request.state.org_id = entry.get("org_id")
        request.state.project_id = entry.get("project_id")
        request.state.is_admin = entry.get("is_admin", False)

        caller_org = request.headers.get("x-caller-organization")
        if caller_org and entry.get("is_admin"):
            try:
                request.state.org_id = int(caller_org)
            except (ValueError, TypeError):
                pass

        request.state.organization_id = request.state.org_id
        return await call_next(request)

