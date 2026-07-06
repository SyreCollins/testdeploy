import logging

from anthropic import AsyncAnthropic

from app.ai.gateway.base import BaseModelProvider, ModelResponse, StreamEvent

logger = logging.getLogger("zam-ai-core-api.claude-gateway")


class ClaudeProvider(BaseModelProvider):
    provider_name = "claude"

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        self._model = model
        self._client = AsyncAnthropic(api_key=api_key)
        logger.info(f"Initialized ClaudeProvider (model={model})")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ) -> ModelResponse:
        params = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        params.update(kwargs)
        if system_prompt:
            params["system"] = system_prompt

        resp = await self._client.messages.create(**params)

        return ModelResponse(
            text=resp.content[0].text,
            provider=self.provider_name,
            model=self._model,
            finish_reason=resp.stop_reason or "stop",
            usage={
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            },
            raw=resp.model_dump(),
        )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ):
        params = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        params.update(kwargs)
        if system_prompt:
            params["system"] = system_prompt

        async with self._client.messages.stream(**params) as stream:
            async for text_delta in stream.text_stream:
                yield StreamEvent(type="delta", text=text_delta)

            final = await stream.get_final_message()
            yield StreamEvent(
                type="done",
                finish_reason=final.stop_reason or "stop",
                usage={
                    "input_tokens": final.usage.input_tokens,
                    "output_tokens": final.usage.output_tokens,
                },
            )
