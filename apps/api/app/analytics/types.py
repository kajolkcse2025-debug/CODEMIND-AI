"""Plain data types for the analytics engine.

This package is PURE: no database, no network, no FastAPI, no AI. Inputs are plain
dataclasses, outputs are plain dataclasses. That is what keeps scoring reproducible and
cheap to test (blueprint sections 5.1 and 8.4).
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

ENGINE_VERSION = 0  # 0 means "interfaces only": no scoring formula is implemented yet.

Difficulty = Literal["easy", "medium", "hard"]
AttemptOutcome = Literal["in_progress", "accepted", "failed", "abandoned"]

# Canonical trait and weakness vocabularies (the database CHECK constraints must match these).
DNA_TRAITS: tuple[str, ...] = (
    "logical_reasoning",
    "debugging",
    "optimization",
    "edge_case_awareness",
    "time_management",
    "hint_independence",
    "consistency",
    "recursion_ability",
)

WEAKNESS_CODES: tuple[str, ...] = (
    "off_by_one",
    "edge_case_failure",
    "recursion_mistake",
    "graph_traversal_mistake",
    "dp_struggle",
    "optimization_gap",
    "incorrect_complexity_analysis",
    "repeated_failed_attempts",
    "excessive_hint_usage",
    "slow_solving",
)


class MetricState(StrEnum):
    """How much a number can be trusted. UNAVAILABLE means: do not show a score."""

    UNAVAILABLE = "unavailable"
    CALIBRATING = "calibrating"
    PROVISIONAL = "provisional"
    ESTABLISHED = "established"


@dataclass(frozen=True)
class AttemptFact:
    """One closed attempt, as the analytics engine sees it.

    ``verified`` is True only when a real sandboxed runner produced the result. Unverified
    attempts are excluded from every metric by ``verified_only``.
    """

    attempt_id: str
    topic_slug: str
    difficulty: Difficulty
    outcome: AttemptOutcome
    verified: bool
    hints_used: int = 0
    active_time_sec: int = 0
    expected_time_sec: int = 0


@dataclass(frozen=True)
class SubmissionFact:
    submission_id: str
    topic_slug: str
    verdict: str
    verified: bool
    failed_test_tags: tuple[str, ...] = ()


def verified_only(attempts: Iterable[AttemptFact]) -> list[AttemptFact]:
    """The single gate that keeps unverified runs out of mastery, XP, DNA and readiness."""
    return [a for a in attempts if a.verified and a.outcome != "in_progress"]


def verified_submissions(submissions: Sequence[SubmissionFact]) -> list[SubmissionFact]:
    return [s for s in submissions if s.verified and s.verdict != "runner_unavailable"]
