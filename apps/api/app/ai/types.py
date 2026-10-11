from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class ModelTier(StrEnum):
    """Model names live in configuration; features only ask for a tier."""

    FAST = "fast"
    STRONG = "strong"


@dataclass(frozen=True)
class AIMessage:
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass(frozen=True)
class AIUsage:
    tokens_in: int = 0
    tokens_out: int = 0


@dataclass(frozen=True)
class AIResponse:
    text: str
    provider: str
    model: str
    usage: AIUsage = AIUsage()
