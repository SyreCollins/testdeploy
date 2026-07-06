from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class ModelResponse:
    text: str
    provider: str
    model: str
    finish_reason: str = "stop"
    usage: dict | None = None
    raw: dict | None = field(default=None, repr=False)


@dataclass
class StreamEvent:
    type: str
    text: str = ""
    finish_reason: str | None = None
    usage: dict | None = None


class BaseModelProvider(ABC):
    provider_name: str = ""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ) -> ModelResponse:
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        **kwargs,
    ) -> AsyncIterator[StreamEvent]:
        pass
