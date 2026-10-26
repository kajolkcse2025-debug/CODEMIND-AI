
"""Select a balanced set of questions for a coding assessment."""

import random
from collections import Counter

from app.services.coding_assessment_bank import (
    QUESTION_BANK,
    CodingAssessmentQuestion,
)


ASSESSMENT_TOPICS = (
    "arrays",
    "strings",
    "hashing",
    "sliding-window",
    "two-pointer",
    "binary-search",
    "linked-list",
    "dynamic-programming",
)


def select_assessment_questions(
    questions: tuple[CodingAssessmentQuestion, ...] = QUESTION_BANK,
    question_count: int = 8,
    rng: random.Random | None = None,
) -> list[CodingAssessmentQuestion]:
    """Choose distinct questions while covering as many topics as possible."""

    if question_count < 1:
        raise ValueError("question_count must be at least 1.")

    if question_count > len(questions):
        raise ValueError(
            "question_count cannot exceed the number of available questions."
        )

    if not questions:
        raise ValueError("The question bank is empty.")

    randomizer = rng if rng is not None else random.Random()

    # Group questions by topic.
    questions_by_topic: dict[str, list[CodingAssessmentQuestion]] = {}

    for question in questions:
        questions_by_topic.setdefault(question.topic_slug, []).append(question)

    # Shuffle each group so selection can vary between assessments.
    for topic_questions in questions_by_topic.values():
        randomizer.shuffle(topic_questions)

    # Randomize the topic order too.
    available_topics = list(questions_by_topic)
    randomizer.shuffle(available_topics)

    selected: list[CodingAssessmentQuestion] = []

    # First pass: take one question from each available topic.
    for topic in available_topics:
        if len(selected) >= question_count:
            break

        selected.append(questions_by_topic[topic].pop())

    # Second pass: fill remaining places without repeating questions.
    remaining = [
        question
        for topic_questions in questions_by_topic.values()
        for question in topic_questions
    ]
    randomizer.shuffle(remaining)

    selected.extend(remaining[: question_count - len(selected)])

    return selected


def summarize_selection(
    questions: list[CodingAssessmentQuestion],
) -> dict[str, dict[str, int]]:
    """Summarize the selected questions by topic and difficulty."""

    return {
        "topics": dict(
            Counter(question.topic_slug for question in questions)
        ),
        "difficulties": dict(
            Counter(question.difficulty for question in questions)
        ),
    }
