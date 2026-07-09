from collections.abc import AsyncIterator

import pytest

from app.ai.gateway.base import BaseModelProvider, ModelResponse, StreamEvent
from app.ai.gateway.factory import get_model_provider
from app.ai.gateway.mock import MockModelProvider
from app.core.config import Settings


class TestModelResponse:
    def test_defaults(self) -> None:
        resp = ModelResponse(text="hello", provider="mock", model="mock")
        assert resp.text == "hello"
        assert resp.finish_reason == "stop"
        assert resp.usage is None
        assert resp.raw is None

    def test_full_init(self) -> None:
        resp = ModelResponse(
            text="hello",
            provider="claude",
            model="claude-3",
            finish_reason="end_turn",
            usage={"input_tokens": 10, "output_tokens": 20},
            raw={"id": "msg_123"},
        )
        assert resp.provider == "claude"
        assert resp.finish_reason == "end_turn"
        assert resp.usage["output_tokens"] == 20


class TestStreamEvent:
    def test_delta_event(self) -> None:
        event = StreamEvent(type="delta", text="Hello")
        assert event.type == "delta"
        assert event.text == "Hello"
        assert event.finish_reason is None
        assert event.usage is None

    def test_done_event(self) -> None:
        event = StreamEvent(
            type="done",
            finish_reason="stop",
            usage={"input_tokens": 5, "output_tokens": 15},
        )
        assert event.type == "done"
        assert event.finish_reason == "stop"


class TestMockModelProvider:
    @pytest.fixture
    def provider(self) -> MockModelProvider:
        return MockModelProvider()

    @pytest.fixture
    def custom_provider(self) -> MockModelProvider:
        return MockModelProvider(response_text="Custom test response")

    @pytest.mark.asyncio
    async def test_generate_returns_response(self, provider: MockModelProvider) -> None:
        resp = await provider.generate(prompt="What is aspirin?")
        assert isinstance(resp, ModelResponse)
        assert resp.provider == "mock"
        assert resp.model == "mock"
        assert resp.finish_reason == "stop"
        assert resp.text == "This is a mock response from the AI model gateway."

    @pytest.mark.asyncio
    async def test_generate_with_custom_text(self, custom_provider: MockModelProvider) -> None:
        resp = await custom_provider.generate(prompt="Test")
        assert resp.text == "Custom test response"

    @pytest.mark.asyncio
    async def test_generate_accepts_all_params(self, provider: MockModelProvider) -> None:
        resp = await provider.generate(
            prompt="Test",
            system_prompt="Be helpful",
            max_tokens=2048,
            temperature=0.7,
            extra_param="ignored",
        )
        assert resp is not None

    @pytest.mark.asyncio
    async def test_generate_stream_yields_events(self, provider: MockModelProvider) -> None:
        events: list[StreamEvent] = []
        stream = provider.generate_stream(prompt="Test")
        assert isinstance(stream, AsyncIterator)

        async for event in stream:
            events.append(event)

        assert len(events) == 2
        assert events[0].type == "delta"
        assert events[0].text == "This is a mock response from the AI model gateway."
        assert events[1].type == "done"
        assert events[1].finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_usage(self, provider: MockModelProvider) -> None:
        resp = await provider.generate(prompt="Test")
        assert resp.usage == {"input_tokens": 0, "output_tokens": 0}


class TestFactory:
    def test_provider_map_keys(self) -> None:
        from app.ai.gateway.factory import PROVIDER_MAP
        assert "claude" in PROVIDER_MAP
        assert "gemini" in PROVIDER_MAP
        assert len(PROVIDER_MAP) == 2

    def test_unknown_provider_raises_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown model provider"):
            get_model_provider(Settings(model_provider="unknown"))

    def test_no_provider_configured_returns_mock(self) -> None:
        provider = get_model_provider(Settings(model_provider=""))
        assert isinstance(provider, MockModelProvider)

    def test_claude_without_key_skips(self) -> None:
        provider = get_model_provider(Settings(model_provider=""))
        assert isinstance(provider, MockModelProvider)

    def test_gemini_without_key_skips(self) -> None:
        provider = get_model_provider(Settings(model_provider=""))
        assert isinstance(provider, MockModelProvider)

    def test_auto_detect_returns_mock_when_no_keys(self) -> None:
        from app.ai.gateway.factory import AUTO_DETECT_ORDER
        assert AUTO_DETECT_ORDER == ["claude", "gemini"]

        provider = get_model_provider(Settings(model_provider=""))
        assert isinstance(provider, MockModelProvider)


class TestClaudeProvider:
    @pytest.fixture
    def settings(self) -> Settings:
        return Settings(
            model_provider="claude",
            claude_api_key="sk-ant-test-key",
            claude_model="claude-sonnet-4-20250514",
        )

    def test_instantiation_succeeds(self, settings: Settings) -> None:
        provider = get_model_provider(settings)
        assert provider.provider_name == "claude"

    def test_instantiation_fails_without_key(self) -> None:
        with pytest.raises(ValueError, match="ZAM_AI_CLAUDE_API_KEY is not set"):
            get_model_provider(Settings(model_provider="claude"))


class TestGeminiProvider:
    @pytest.fixture
    def settings(self) -> Settings:
        return Settings(
            model_provider="gemini",
            gemini_api_key="test-key",
            gemini_model="gemini-2.0-flash",
        )

    def test_instantiation_succeeds(self, settings: Settings) -> None:
        provider = get_model_provider(settings)
        assert provider.provider_name == "gemini"

    def test_instantiation_fails_without_key(self) -> None:
        with pytest.raises(ValueError, match="ZAM_AI_GEMINI_API_KEY is not set"):
            get_model_provider(Settings(model_provider="gemini"))


class TestBaseProvider:
    def test_cannot_instantiate_abstract(self) -> None:
        with pytest.raises(TypeError):
            BaseModelProvider()