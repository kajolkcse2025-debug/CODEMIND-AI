
"""Deterministic hybrid assessment selection and scoring.

This module is intentionally independent of the database, API, and AI provider.
Assessment results describe observed answers, not verified coding mastery.
"""

from dataclasses import dataclass
from typing import Literal

Phase = Literal["structured", "adaptive"]
Difficulty = Literal["easy", "medium", "hard"]


@dataclass(frozen=True)
class AssessmentQuestion:
    id: str
    topic_slug: str
    difficulty: Difficulty
    prompt: str
    options: tuple[str, ...]
    correct_option: str
    explanation: str


@dataclass(frozen=True)
class AnswerEvidence:
    question_id: str
    topic_slug: str
    difficulty: Difficulty
    correct: bool


@dataclass(frozen=True)
class TopicResult:
    topic_slug: str
    correct: int
    answered: int
    accuracy: float | None
    confidence: Literal["low", "moderate", "higher"]


def grade_answer(
    question: AssessmentQuestion, selected_option: str
) -> bool:
    """Compare an answer with the server-side answer key."""
    return selected_option == question.correct_option


def choose_adaptive_difficulty(
    evidence: list[AnswerEvidence], topic_slug: str
) -> Difficulty:
    """Choose a follow-up level using recent evidence for one topic."""
    topic_evidence = [
        item for item in evidence if item.topic_slug == topic_slug
    ]

    if len(topic_evidence) < 2:
        return "easy"

    recent = topic_evidence[-2:]

    if all(item.correct for item in recent):
        return "hard"

    if not any(item.correct for item in recent):
        return "easy"

    return "medium"


def summarize_topic(
    evidence: list[AnswerEvidence], topic_slug: str
) -> TopicResult:
    """Summarize observed answers without claiming verified mastery."""
    topic_evidence = [
        item for item in evidence if item.topic_slug == topic_slug
    ]

    answered = len(topic_evidence)
    correct = sum(item.correct for item in topic_evidence)

    if answered == 0:
        accuracy = None
        confidence = "low"
    else:
        accuracy = correct / answered

        if answered < 3:
            confidence = "low"
        elif answered < 6:
            confidence = "moderate"
        else:
            confidence = "higher"

    return TopicResult(
        topic_slug=topic_slug,
        correct=correct,
        answered=answered,
        accuracy=accuracy,
        confidence=confidence,
    )
