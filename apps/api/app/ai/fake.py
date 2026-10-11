"""Deterministic provider for tests and offline development. Not allowed in production.

It returns only what a test explicitly scripts. It never invents scores or student data.
"""

from collections import deque
from collections.abc import Iterator, Sequence

from pydantic import BaseModel

from app.ai.errors import AIUnavailableError, AIValidationError
from app.ai.provider import T
from app.ai.types import AIMessage, AIResponse, AIUsage, ModelTier

DEFAULT_TEXT = "[fake-ai] This is a scripted placeholder response, not real AI output."


class FakeAIProvider:
    name = "fake"

    def __init__(
        self,
        texts: Sequence[str] = (),
        structured: Sequence[BaseModel] = (),
        *,
        fail_with: Exception | None = None,
    ) -> None:
        self._texts: deque[str] = deque(texts)
        self._structured: deque[BaseModel] = deque(structured)
        self._fail_with = fail_with
        self.calls: list[tuple[str, tuple[AIMessage, ...]]] = []

    def _record(self, kind: str, messages: Sequence[AIMessage]) -> None:
        self.calls.append((kind, tuple(messages)))
        if self._fail_with is not None:
            raise self._fail_with

    def _next_text(self) -> str:
        return self._texts.popleft() if self._texts else DEFAULT_TEXT

    def generate_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> AIResponse:
        self._record("text", messages)
        return AIResponse(text=self._next_text(), provider=self.name, model="fake", usage=AIUsage())

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
        self._record("structured", messages)
        if not self._structured:
            raise AIUnavailableError("FakeAIProvider has no scripted structured response.")
        item = self._structured.popleft()
        if not isinstance(item, schema):
            raise AIValidationError(
                f"Scripted response is {type(item).__name__}, expected {schema.__name__}."
            )
        return item

    def stream_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> Iterator[str]:
        self._record("stream", messages)
        for word in self._next_text().split(" "):
            yield word + " "
