"""Pure analytics engine: deterministic, no I/O. See ``types.py`` for the rules."""

from app.analytics.dna import CodingDna, DnaTrait, calculate_coding_dna
from app.analytics.mastery import TopicMastery, calculate_topic_mastery
from app.analytics.readiness import ComponentScore, ReadinessResult, calculate_readiness
from app.analytics.types import (
    DNA_TRAITS,
    ENGINE_VERSION,
    WEAKNESS_CODES,
    AttemptFact,
    MetricState,
    SubmissionFact,
    verified_only,
)
from app.analytics.weakness import WeaknessCandidate, detect_weaknesses

__all__ = [
    "DNA_TRAITS",
    "ENGINE_VERSION",
    "WEAKNESS_CODES",
    "AttemptFact",
    "CodingDna",
    "ComponentScore",
    "DnaTrait",
    "MetricState",
    "ReadinessResult",
    "SubmissionFact",
    "TopicMastery",
    "WeaknessCandidate",
    "calculate_coding_dna",
    "calculate_readiness",
    "calculate_topic_mastery",
    "detect_weaknesses",
    "verified_only",
]
