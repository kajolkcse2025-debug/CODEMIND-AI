from collections.abc import Sequence
from dataclasses import dataclass

from app.analytics.types import SubmissionFact, verified_submissions


@dataclass(frozen=True)
class WeaknessCandidate:
    code: str
    topic_slug: str | None
    severity: float
    confidence: float
    occurrences: int


def detect_weaknesses(submissions: Sequence[SubmissionFact]) -> list[WeaknessCandidate]:
    """Interface for rule-based weakness detection (blueprint section 11).

    Phase 1 implements no detection rules, so it never invents a weakness. Evidence must come
    from verified submissions only; the gate is applied here so later rules inherit it.
    """
    _evidence = verified_submissions(submissions)
    return []
