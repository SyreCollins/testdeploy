import logging

from google import genai
from google.genai import types as genai_types

from app.ai.gateway.base import BaseModelProvider, ModelResponse, StreamEvent

logger = logging.getLogger("zam-ai-core-api.gemini-gateway")


class GeminiProvider(BaseModelProvider):
    provider_name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
    ) -> None:
        self._model = model
        self._client = genai.Client(api_key=api_key)
        logger.info(f"Initialized GeminiProvider (model={model})")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ) -> ModelResponse:
        config = genai_types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_prompt,
        )
        resp = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config,
        )

        return ModelResponse(
            text=resp.text or "",
            provider=self.provider_name,
            model=self._model,
            finish_reason=(
                resp.candidates[0].finish_reason.name if resp.candidates else "unknown"
            ),
            usage=(
                {
                    "input_tokens": resp.usage_metadata.prompt_token_count,
                    "output_tokens": resp.usage_metadata.candidates_token_count,
                }
                if resp.usage_metadata
                else None
            ),
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
        config = genai_types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_prompt,
        )
        stream = await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=prompt,
            config=config,
        )

        async for chunk in stream:
            if chunk.text:
                yield StreamEvent(type="delta", text=chunk.text)

            if chunk.candidates and chunk.candidates[0].finish_reason:
                yield StreamEvent(
                    type="done",
                    finish_reason=chunk.candidates[0].finish_reason.name,
                    usage=(
                        {
                            "input_tokens": chunk.usage_metadata.prompt_token_count,
                            "output_tokens": chunk.usage_metadata.candidates_token_count,
                        }
                        if chunk.usage_metadata
                        else None
                    ),
                )
