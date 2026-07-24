import json
from datetime import UTC, datetime

from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.db.models.usage import UsageRecord

_AI_PREFIX = "/v1/ai/"


class UsageTracker(BaseHTTPMiddleware):
    def __init__(self, app, engine) -> None:
        super().__init__(app)
        self._engine = engine

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        path = request.url.path
        if not path.startswith(_AI_PREFIX):
            return response

        organization_id = getattr(request.state, "org_id", None) or getattr(request.state, "organization_id", None)
        if organization_id is None:
            return response

        api_key_entry = getattr(request.state, "api_key_entry", None)
        api_key_id = api_key_entry.get("id") if api_key_entry else None

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        response = Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        completion_tokens = 0
        if response.status_code == 200:
            try:
                data = json.loads(response_body)
                result = data.get("result") or {}
                answer = result.get("answer", "")
                completion_tokens = max(1, len(answer) // 4)
            except (json.JSONDecodeError, AttributeError, TypeError):
                pass

        content_length = request.headers.get("content-length")
        prompt_tokens = max(1, int(content_length) // 4) if content_length else 1

        self._write_usage(
            organization_id=organization_id,
            api_key_id=api_key_id,
            endpoint=path,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        return response

    def _write_usage(
        self,
        organization_id: int,
        api_key_id: str | None,
        endpoint: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        with Session(self._engine) as session:
            record = UsageRecord(
                organization_id=organization_id,
                api_key_id=api_key_id,
                date=today,
                endpoint=endpoint,
                request_count=1,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            session.add(record)
            session.commit()
