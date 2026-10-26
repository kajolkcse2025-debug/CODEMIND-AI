
from app.services.coding_assessment_bank import (
    QUESTION_BANK,
    validate_question_bank,
)


def test_question_bank_has_eight_questions():
    assert len(QUESTION_BANK) == 8


def test_question_slugs_are_unique():
    slugs = [question.slug for question in QUESTION_BANK]
    assert len(slugs) == len(set(slugs))


def test_question_bank_validation_passes():
    assert validate_question_bank(QUESTION_BANK) == []


def test_every_topic_is_represented_once():
    topics = [question.topic_slug for question in QUESTION_BANK]
    assert set(topics) == {
        "arrays",
        "strings",
        "hashing",
        "sliding-window",
        "two-pointer",
        "binary-search",
        "linked-list",
        "dynamic-programming",
    }
    assert len(topics) == len(set(topics))


def test_each_question_has_multiple_test_cases():
    assert all(len(question.test_cases) >= 3 for question in QUESTION_BANK)


def test_test_cases_have_input_and_expected_output():
    for question in QUESTION_BANK:
        for case in question.test_cases:
            assert isinstance(case.stdin, str)
            assert case.expected_stdout.strip() != ""


def test_difficulty_and_time_metadata_are_valid():
    for question in QUESTION_BANK:
        assert question.difficulty in {"easy", "medium", "hard"}
        assert question.expected_time_sec > 0
        assert question.diagnostic_level in {1, 2, 3}
