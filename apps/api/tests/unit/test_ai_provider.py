import pytest
from pydantic import BaseModel, SecretStr

from app.ai import (
    AIMessage,
    AIUnavailableError,
    AIValidationError,
    FakeAIProvider,
    GeminiProvider,
    ModelTier,
    build_ai_provider,
)
from app.ai.fake import DEFAULT_TEXT
from app.config import Settings

MESSAGES = [AIMessage("user", "Explain binary search")]


class Explanation(BaseModel):
    summary: str


def test_fake_provider_is_scripted_and_records_calls() -> None:
    provider = FakeAIProvider(texts=["first", "second"])
    assert provider.generate_text(MESSAGES).text == "first"
    assert provider.generate_text(MESSAGES).text == "second"
    assert provider.generate_text(MESSAGES).text == DEFAULT_TEXT
    assert [kind for kind, _ in provider.calls] == ["text", "text", "text"]


def test_fake_provider_text_is_clearly_labelled_as_fake() -> None:
    assert FakeAIProvider().generate_text(MESSAGES).text.startswith("[fake-ai]")


def test_fake_provider_structured_returns_scripted_object() -> None:
    provider = FakeAIProvider(structured=[Explanation(summary="ok")])
    assert provider.generate_structured(MESSAGES, Explanation).summary == "ok"


def test_fake_provider_structured_without_script_is_unavailable_not_invented() -> None:
    with pytest.raises(AIUnavailableError):
        FakeAIProvider().generate_structured(MESSAGES, Explanation)


def test_fake_provider_rejects_wrong_schema() -> None:
    class Other(BaseModel):
        value: int

    with pytest.raises(AIValidationError):
        FakeAIProvider(structured=[Explanation(summary="x")]).generate_structured(MESSAGES, Other)


def test_fake_provider_streams_words() -> None:
    provider = FakeAIProvider(texts=["hello brave world"])
    assert "".join(provider.stream_text(MESSAGES)).strip() == "hello brave world"


def test_fake_provider_can_simulate_outage() -> None:
    provider = FakeAIProvider(fail_with=AIUnavailableError("down"))
    with pytest.raises(AIUnavailableError):
        provider.generate_text(MESSAGES)


def test_gemini_provider_makes_no_calls_and_fails_loudly() -> None:
    provider = GeminiProvider(SecretStr("key"), "fast-model", "strong-model")
    assert provider.configured is True
    with pytest.raises(AIUnavailableError):
        provider.generate_text(MESSAGES, tier=ModelTier.STRONG)
    with pytest.raises(AIUnavailableError):
        provider.generate_structured(MESSAGES, Explanation)
    with pytest.raises(AIUnavailableError):
        list(provider.stream_text(MESSAGES))


def test_gemini_provider_reports_unconfigured() -> None:
    assert GeminiProvider(None).configured is False


def test_factory_selects_provider_from_settings() -> None:
    base = {"database_url": "postgresql://u:p@h/d", "redis_url": "redis://x"}
    assert build_ai_provider(Settings(_env_file=None, **base)).name == "gemini"  # type: ignore[arg-type]
    fake = Settings(_env_file=None, ai_provider="fake", **base)  # type: ignore[arg-type]
    assert build_ai_provider(fake).name == "fake"
