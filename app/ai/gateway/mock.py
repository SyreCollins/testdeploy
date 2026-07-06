import logging
from collections.abc import AsyncIterator

from app.ai.gateway.base import BaseModelProvider, ModelResponse, StreamEvent

logger = logging.getLogger("zam-ai-core-api.mock-gateway")


class MockModelProvider(BaseModelProvider):
    provider_name = "mock"

    def __init__(self, response_text: str | None = None) -> None:
        self._response_text = response_text or "This is a mock response from the AI model gateway."
        logger.warning("Using MockModelProvider — not for production")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ) -> ModelResponse:
        return ModelResponse(
            text=self._response_text,
            provider=self.provider_name,
            model="mock",
            finish_reason="stop",
            usage={"input_tokens": 0, "output_tokens": 0},
        )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ) -> AsyncIterator[StreamEvent]:
        yield StreamEvent(type="delta", text=self._response_text)
        yield StreamEvent(type="done", finish_reason="stop", usage={"input_tokens": 0, "output_tokens": 0})
