
from app.services.assessment_engine import (
    AnswerEvidence,
    AssessmentQuestion,
    choose_adaptive_difficulty,
    grade_answer,
    summarize_topic,
)


def evidence(correct: bool, topic: str = "arrays") -> AnswerEvidence:
    return AnswerEvidence(
        question_id=f"q-{correct}",
        topic_slug=topic,
        difficulty="easy",
        correct=correct,
    )


def test_answer_is_graded_correctly() -> None:
    question = AssessmentQuestion(
        id="arrays-1",
        topic_slug="arrays",
        difficulty="easy",
        prompt="Which option is correct?",
        options=("A", "B", "C", "D"),
        correct_option="B",
        explanation="B is correct.",
    )

    assert grade_answer(question, "B") is True
    assert grade_answer(question, "A") is False


def test_adaptive_starts_easy_without_enough_evidence() -> None:
    assert choose_adaptive_difficulty([], "arrays") == "easy"


def test_two_correct_answers_raise_difficulty() -> None:
    history = [evidence(True), evidence(True)]

    assert choose_adaptive_difficulty(history, "arrays") == "hard"


def test_two_wrong_answers_keep_difficulty_easy() -> None:
    history = [evidence(False), evidence(False)]

    assert choose_adaptive_difficulty(history, "arrays") == "easy"


def test_adaptive_selection_ignores_other_topics() -> None:
    history = [evidence(True, "strings"), evidence(True, "strings")]

    assert choose_adaptive_difficulty(history, "arrays") == "easy"


def test_insufficient_evidence_has_low_confidence() -> None:
    result = summarize_topic([evidence(True)], "arrays")

    assert result.correct == 1
    assert result.answered == 1
    assert result.accuracy == 1.0
    assert result.confidence == "low"


def test_no_answers_produce_no_accuracy() -> None:
    result = summarize_topic([], "arrays")

    assert result.accuracy is None
    assert result.confidence == "low"
