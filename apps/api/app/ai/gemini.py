"""Gemini provider: configuration only in Phase 1.

It deliberately makes NO network call and imports NO Google SDK yet. Every method raises
``AIUnavailableError`` so a misconfigured deployment fails loudly instead of returning
invented content. The real implementation arrives with the AI coach phase.
"""

from collections.abc import Iterator, Sequence

from pydantic import SecretStr

from app.ai.errors import AIUnavailableError
from app.ai.provider import T
from app.ai.types import AIMessage, AIResponse, ModelTier

_MESSAGE = "GeminiProvider is not implemented yet; it is scheduled for the AI coach phase."


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        api_key: SecretStr | None,
        model_fast: str | None = None,
        model_strong: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._models = {ModelTier.FAST: model_fast, ModelTier.STRONG: model_strong}

    @property
    def configured(self) -> bool:
        return self._api_key is not None and all(self._models.values())

    def generate_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> AIResponse:
        raise AIUnavailableError(_MESSAGE)

    def generate_structured(
        self,
        messages: Sequence[AIMessage],
        schema: type[T],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.0,
        timeout_s: float = 30.0,
    ) -> T:
        raise AIUnavailableError(_MESSAGE)

    def stream_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> Iterator[str]:
        raise AIUnavailableError(_MESSAGE)
