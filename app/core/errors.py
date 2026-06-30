from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.core.request_context import get_request_id


class ApiError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        retryable: bool = False,
        details: dict | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.details = details or {}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "request_id": get_request_id(request),
                "status": "error",
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "retryable": exc.retryable,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request.app.state.logger.exception(
            "unhandled_error",
            extra={"request_id": get_request_id(request), "error_type": type(exc).__name__},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": get_request_id(request),
                "status": "error",
                "error": {
                    "code": "internal_error",
                    "message": "An internal error occurred.",
                    "retryable": False,
                    "details": {},
                },
            },
        )

