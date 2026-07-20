import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    SENSITIVE_HEADERS = {"authorization", "x-zam-ai-key", "cookie", "set-cookie"}

    async def dispatch(self, request: Request, call_next) -> Response:
        logger = request.app.state.logger

        request_id = getattr(request.state, "request_id", None)
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""

        safe_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in self.SENSITIVE_HEADERS
        }
        logger.info(
            "request_started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_string": str(request.url.query),
                "headers": safe_headers,
                "body": body_str[:10000],
            },
        )

        started_at = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "latency_ms": elapsed_ms,
                    "error": str(exc),
                },
            )
            raise

        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)

        response_body = b""
        if response.headers.get("content-type", "").startswith("application/json"):
            async for chunk in response.body_iterator:
                response_body += chunk
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
            response_body_str = response_body.decode("utf-8", errors="replace")[:10000]
        else:
            response_body_str = f"<{response.headers.get('content-type', 'unknown')}>"

        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": elapsed_ms,
                "response_body": response_body_str,
            },
        )

        return response
