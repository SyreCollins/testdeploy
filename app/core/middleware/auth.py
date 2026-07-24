import time
from collections.abc import Callable

import httpx
import jwt
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.request_context import get_request_id

_JWKS_CACHE: dict[str, list[dict]] = {}
_JWKS_CACHE_AT = 0.0
_JWKS_CACHE_TTL = 300


class ClerkAuthMiddleware(BaseHTTPMiddleware):
    _PUBLIC_PATHS = {"/v1/health", "/v1/auth/webhook", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self._PUBLIC_PATHS:
            return await call_next(request)

        if getattr(request.state, "api_key_entry", None) is not None:
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "request_id": get_request_id(request),
                    "status": "error",
                    "error": {
                        "code": "authentication_failed",
                        "message": "Invalid or missing authentication token.",
                        "retryable": False,
                        "details": {},
                    },
                },
            )

        token = auth_header[7:]

        try:
            payload = _verify_clerk_jwt(token)
            if payload is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "request_id": get_request_id(request),
                        "status": "error",
                        "error": {
                            "code": "authentication_failed",
                            "message": "Invalid or expired authentication token.",
                            "retryable": False,
                            "details": {},
                        },
                    },
                )

            request.state.auth_type = "clerk_jwt"
            request.state.clerk_user_id = payload.get("sub")
            request.state.organization_id = _extract_org_id(payload)
            request.state.clerk_session_id = payload.get("sid")
            request.state.clerk_jwt_payload = payload

        except Exception:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "request_id": get_request_id(request),
                    "status": "error",
                    "error": {
                        "code": "authentication_failed",
                        "message": "Invalid or malformed authentication token.",
                        "retryable": False,
                        "details": {},
                    },
                },
            )

        return await call_next(request)


def _extract_org_id(payload: dict) -> int | None:
    org_id = payload.get("org_id")
    if org_id is not None:
        try:
            return int(org_id)
        except (ValueError, TypeError):
            return None
    return None


def _verify_clerk_jwt(token: str) -> dict | None:
    try:
        unverified_header = jwt.get_unverified_header(token)
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
    except Exception:
        return None

    kid = unverified_header.get("kid")
    issuer = unverified_payload.get("iss")
    if not kid or not issuer:
        return None

    keys = _fetch_jwks(issuer)
    if not keys:
        return None

    jwk = next((k for k in keys if k.get("kid") == kid), None)
    if not jwk:
        return None

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={"verify_exp": True},
        )
        return payload
    except jwt.PyJWTError:
        return None


def _fetch_jwks(issuer: str) -> list[dict]:
    global _JWKS_CACHE_AT
    now = time.time()
    if _JWKS_CACHE and now - _JWKS_CACHE_AT < _JWKS_CACHE_TTL:
        return _JWKS_CACHE.get("default", [])

    jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
    try:
        response = httpx.get(jwks_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        keys = data.get("keys", [])
        _JWKS_CACHE["default"] = keys
        _JWKS_CACHE_AT = now
        return keys
    except Exception:
        return _JWKS_CACHE.get("default", [])
