"""The provider seam. Nothing outside ``app/ai`` may import a vendor SDK.

AI writes language (explanations, hints, coaching). It must never produce a score: every
number the student sees is computed by the analytics engine.
"""

from collections.abc import Iterator, Sequence
from typing import Protocol, TypeVar

from pydantic import BaseModel

from app.ai.types import AIMessage, AIResponse, ModelTier

T = TypeVar("T", bound=BaseModel)


class AIProvider(Protocol):
    name: str

    def generate_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> AIResponse: ...

    def generate_structured(
        self,
        messages: Sequence[AIMessage],
        schema: type[T],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.0,
        timeout_s: float = 30.0,
    ) -> T: ...

    def stream_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> Iterator[str]: ...
