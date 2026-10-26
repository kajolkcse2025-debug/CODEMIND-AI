
import random

import pytest

from app.services.coding_assessment_bank import QUESTION_BANK
from app.services.coding_assessment_selector import (
    select_assessment_questions,
    summarize_selection,
)


def test_selector_returns_requested_number_of_questions():
    result = select_assessment_questions(question_count=5)

    assert len(result) == 5


def test_selector_does_not_repeat_questions():
    result = select_assessment_questions(question_count=8)

    slugs = [question.slug for question in result]

    assert len(slugs) == len(set(slugs))


def test_selector_covers_distinct_topics_when_possible():
    result = select_assessment_questions(question_count=5)

    topics = [question.topic_slug for question in result]

    assert len(topics) == len(set(topics))


def test_selector_can_select_all_questions():
    result = select_assessment_questions(
        question_count=len(QUESTION_BANK)
    )

    assert {question.slug for question in result} == {
        question.slug for question in QUESTION_BANK
    }


def test_selector_rejects_zero_questions():
    with pytest.raises(ValueError):
        select_assessment_questions(question_count=0)


def test_selector_rejects_more_questions_than_available():
    with pytest.raises(ValueError):
        select_assessment_questions(
            question_count=len(QUESTION_BANK) + 1
        )


def test_selector_rejects_empty_bank():
    with pytest.raises(ValueError):
        select_assessment_questions(questions=(), question_count=1)


def test_same_random_seed_produces_same_selection():
    first = select_assessment_questions(
        question_count=5,
        rng=random.Random(42),
    )
    second = select_assessment_questions(
        question_count=5,
        rng=random.Random(42),
    )

    assert [q.slug for q in first] == [q.slug for q in second]


def test_summary_reports_topics_and_difficulties():
    result = select_assessment_questions(question_count=8)
    summary = summarize_selection(result)

    assert sum(summary["topics"].values()) == 8
    assert sum(summary["difficulties"].values()) == 8
