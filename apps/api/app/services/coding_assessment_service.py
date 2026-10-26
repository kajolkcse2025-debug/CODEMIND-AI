"""Evaluate coding assessment submissions using the existing code runner."""

from app.core.errors import NotFoundError, ServiceUnavailableError
from app.integrations.code_runner import build_code_runner
from app.integrations.code_runner.base import (
    RunRequest,
    RunTestCase,
    Verdict,
)
from app.services.coding_assessment_bank import QUESTION_BANK


class CodingAssessmentService:
    """Run submitted code against assessment question test cases."""

    def submit_code(
        self,
        slug: str,
        language: str,
        source_code: str,
    ) -> dict:
        # 1. Find the assessment question.
        question = next(
            (item for item in QUESTION_BANK if item.slug == slug),
            None,
        )

        if question is None:
            raise NotFoundError(
                "Coding assessment question not found.",
                code="assessment_question_not_found",
            )

        # 2. Convert the question's test cases into runner test cases.
        test_cases = [
            RunTestCase(
                stdin=case.stdin,
                expected_stdout=case.expected_stdout,
                tags=(f"case_{index}",),
            )
            for index, case in enumerate(question.test_cases, start=1)
        ]

        # 3. Execute through the existing sandboxed runner.
        runner = build_code_runner()

        try:
            result = runner.run(
                RunRequest(
                    language=language,
                    source_code=source_code,
                    test_cases=test_cases,
                )
            )
        finally:
            close_runner = getattr(runner, "close", None)
            if callable(close_runner):
                close_runner()

        # 4. Never treat unverified results as successful.
        if (
            result.verdict is Verdict.RUNNER_UNAVAILABLE
            or not result.verified
        ):
            raise ServiceUnavailableError(
                "The code runner could not verify this submission. "
                "Please try again."
            )

        # 5. Give the student a clear result.
        if result.verdict is Verdict.ACCEPTED:
            detail = "All tests passed."
        elif result.verdict is Verdict.WRONG_ANSWER:
            detail = "Some tests failed. Review your solution and try again."
        elif result.verdict is Verdict.COMPILE_ERROR:
            detail = "Your code has a compilation error. Check its syntax."
        elif result.verdict is Verdict.TIME_LIMIT:
            detail = "Your code exceeded the time limit."
        elif result.verdict is Verdict.MEMORY_LIMIT:
            detail = "Your code exceeded the memory limit."
        else:
            detail = (
                "Your code could not complete successfully. "
                "Check your code and try again."
            )

        return {
            "question_slug": question.slug,
            "verdict": result.verdict.value,
            "verified": result.verified,
            "counts_toward_metrics": result.counts_toward_metrics,
            "tests_passed": result.tests_passed,
            "tests_total": result.tests_total,
            "detail": detail,
        }