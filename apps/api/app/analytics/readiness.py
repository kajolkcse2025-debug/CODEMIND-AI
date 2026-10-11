from collections.abc import Mapping
from dataclasses import dataclass

from app.analytics.mastery import NOT_IMPLEMENTED
from app.analytics.types import ENGINE_VERSION, MetricState


@dataclass(frozen=True)
class ComponentScore:
    score: float  # 0..1
    confidence: float  # 0..1


@dataclass(frozen=True)
class ReadinessResult:
    score: int | None  # 0..1000 once implemented
    score_range: tuple[int, int] | None
    provisional: bool
    coverage: float
    state: MetricState
    reason: str
    engine_version: int = ENGINE_VERSION


def calculate_readiness(components: Mapping[str, ComponentScore]) -> ReadinessResult:
    """Interface for interview readiness (blueprint section 15).

    Always unavailable in Phase 1. It is never a hiring probability, and it never will be.
    """
    del components
    return ReadinessResult(
        score=None,
        score_range=None,
        provisional=True,
        coverage=0.0,
        state=MetricState.UNAVAILABLE,
        reason=NOT_IMPLEMENTED,
    )
