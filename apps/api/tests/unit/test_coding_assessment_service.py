import pytest

from app.core.errors import NotFoundError, ServiceUnavailableError
from app.integrations.code_runner.base import RunResult, Verdict
from app.services import coding_assessment_service as assessment_module
from app.services.coding_assessment_bank import QUESTION_BANK
from app.services.coding_assessment_service import CodingAssessmentService


class FakeRunner:
    def __init__(self, result):
        self.result = result
        self.closed = False
        self.request = None

    def run(self, request):
        self.request = request
        return self.result

    def close(self):
        self.closed = True


def test_accepted_submission_returns_verified_result(monkeypatch):
    runner = FakeRunner(
        RunResult(
            verdict=Verdict.ACCEPTED,
            verified=True,
            tests_passed=3,
            tests_total=3,
        )
    )
    monkeypatch.setattr(
        assessment_module, "build_code_runner", lambda: runner
    )

    question = QUESTION_BANK[0]
    result = CodingAssessmentService().submit_code(
        question.slug, "python", "print('test')"
    )

    assert result["verdict"] == "accepted"
    assert result["verified"] is True
    assert result["counts_toward_metrics"] is True
    assert result["tests_passed"] == 3
    assert result["tests_total"] == 3
    assert runner.closed is True
    assert len(runner.request.test_cases) == len(question.test_cases)


def test_wrong_answer_does_not_count_toward_metrics(monkeypatch):
    runner = FakeRunner(
        RunResult(
            verdict=Verdict.WRONG_ANSWER,
            verified=True,
            tests_passed=1,
            tests_total=3,
        )
    )
    monkeypatch.setattr(
        assessment_module, "build_code_runner", lambda: runner
    )

    result = CodingAssessmentService().submit_code(
        QUESTION_BANK[0].slug, "python", "print('wrong')"
    )

    assert result["verdict"] == "wrong_answer"
    assert result["counts_toward_metrics"] is False
    assert runner.closed is True


def test_unavailable_runner_raises_service_error(monkeypatch):
    runner = FakeRunner(
        RunResult(
            verdict=Verdict.RUNNER_UNAVAILABLE,
            verified=False,
        )
    )
    monkeypatch.setattr(
        assessment_module, "build_code_runner", lambda: runner
    )

    with pytest.raises(ServiceUnavailableError):
        CodingAssessmentService().submit_code(
            QUESTION_BANK[0].slug, "python", "print('test')"
        )

    assert runner.closed is True


def test_unknown_question_raises_not_found_without_running(monkeypatch):
    def should_not_run():
        pytest.fail("Runner must not be created for an unknown question")

    monkeypatch.setattr(
        assessment_module, "build_code_runner", should_not_run
    )

    with pytest.raises(NotFoundError):
        CodingAssessmentService().submit_code(
            "not-a-real-question", "python", "print('test')"
        )


def test_unverified_accepted_result_is_rejected(monkeypatch):
    runner = FakeRunner(
        RunResult(
            verdict=Verdict.ACCEPTED,
            verified=False,
            tests_passed=3,
            tests_total=3,
        )
    )
    monkeypatch.setattr(
        assessment_module, "build_code_runner", lambda: runner
    )

    with pytest.raises(ServiceUnavailableError):
        CodingAssessmentService().submit_code(
            QUESTION_BANK[0].slug, "python", "print('test')"
        )

    assert runner.closed is True
