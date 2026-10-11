from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from app.analytics.types import ENGINE_VERSION, AttemptFact, MetricState, verified_only

NOT_IMPLEMENTED = "scoring_not_implemented"
NO_EVIDENCE = "no_verified_evidence"


@dataclass(frozen=True)
class TopicMastery:
    topic_slug: str
    score: float | None
    confidence: float
    state: MetricState
    evidence_count: int
    reason: str
    engine_version: int = ENGINE_VERSION


def calculate_topic_mastery(
    topic_slug: str, attempts: Sequence[AttemptFact], *, now: datetime
) -> TopicMastery:
    """Interface for topic mastery (blueprint section 10).

    Phase 1 intentionally implements NO formula, so it never returns a score. It does apply
    the verified-only gate for real, so the rule is enforced from day one.
    """
    del now  # used by the recency weighting once the formula is implemented
    evidence = [a for a in verified_only(attempts) if a.topic_slug == topic_slug]
    return TopicMastery(
        topic_slug=topic_slug,
        score=None,
        confidence=0.0,
        state=MetricState.UNAVAILABLE,
        evidence_count=len(evidence),
        reason=NOT_IMPLEMENTED if evidence else NO_EVIDENCE,
    )
