from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from app.analytics.mastery import NO_EVIDENCE, NOT_IMPLEMENTED
from app.analytics.types import DNA_TRAITS, ENGINE_VERSION, AttemptFact, MetricState, verified_only


@dataclass(frozen=True)
class DnaTrait:
    trait: str
    score: float | None
    confidence: float
    state: MetricState
    sample_count: int
    reason: str


@dataclass(frozen=True)
class CodingDna:
    traits: tuple[DnaTrait, ...]
    engine_version: int = ENGINE_VERSION


def calculate_coding_dna(attempts: Sequence[AttemptFact], *, now: datetime) -> CodingDna:
    """Interface for Coding DNA (blueprint section 9). Phase 1 never returns a trait score."""
    del now
    evidence_count = len(verified_only(attempts))
    reason = NOT_IMPLEMENTED if evidence_count else NO_EVIDENCE
    return CodingDna(
        traits=tuple(
            DnaTrait(
                trait=name,
                score=None,
                confidence=0.0,
                state=MetricState.UNAVAILABLE,
                sample_count=0,
                reason=reason,
            )
            for name in DNA_TRAITS
        )
    )
