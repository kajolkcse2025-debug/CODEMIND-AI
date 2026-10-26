
from unittest import result

from app.core.errors import NotFoundError
from app.repositories.problems import ProblemsRepository

from app.core.errors import ServiceUnavailableError
from app.integrations.code_runner import build_code_runner
from app.integrations.code_runner.base import RunRequest, RunTestCase, Verdict
from app.schemas.submissions import SubmissionCreate, SubmissionResult

from app.schemas.problems import (
    ProblemDetail,
    ProblemListItem,
    ProblemListResponse,
)


class ProblemsService:
    def __init__(self, repository: ProblemsRepository) -> None:
        self._repository = repository

    def list_problems(
        self,
        difficulty: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ProblemListResponse:
        problems = self._repository.list_published(
            difficulty=difficulty,
            limit=limit,
            offset=offset,
        )

        return ProblemListResponse(
            items=[ProblemListItem.model_validate(p) for p in problems],
            limit=limit,
            offset=offset,
        )

    def get_problem(self, slug: str) -> ProblemDetail:
        problem = self._repository.get_published_by_slug(slug)

        if problem is None:
            raise NotFoundError(
                "Coding problem not found.",
                code="problem_not_found",
            )

        return ProblemDetail.model_validate(problem)
        
    def submit_code(
        self, slug: str, payload: SubmissionCreate
    ) -> SubmissionResult:
        problem = self._repository.get_published_by_slug(slug)

        if problem is None:
            raise NotFoundError(
                "Coding problem not found.",
                code="problem_not_found",
            )

        stored_cases = self._repository.get_test_cases(
            problem.id, problem.version
        )

        if not stored_cases:
            raise ServiceUnavailableError(
                "This problem is not ready for code execution."
            )

        test_cases = [
            RunTestCase(
                stdin=case.stdin,
                expected_stdout=case.expected_stdout,
                tags=(f"case_{case.case_index}",),
            )
            for case in stored_cases
        ]    

        runner = build_code_runner()

        try:
            result = runner.run(
                RunRequest(
                    language=payload.language,
                    source_code=payload.source_code,
                    test_cases=test_cases,
                )
            )
        finally:
            close_runner = getattr(runner, "close", None)
            if callable(close_runner):
                close_runner()

        if result.verdict is Verdict.RUNNER_UNAVAILABLE or not result.verified:
            raise ServiceUnavailableError(
                "The code runner could not verify this submission. Please try again."
            )

        if result.verdict is Verdict.ACCEPTED:
            detail = "All tests passed."
        elif result.verdict is Verdict.WRONG_ANSWER:
            detail = "Some tests did not pass. Review your code and try again."
        else:
            detail = (
                "Your code could not complete successfully. "
                "Check your code and try again."
            )

        return SubmissionResult(
            verdict=result.verdict.value,
            verified=result.verified,
            tests_passed=result.tests_passed,
            tests_total=result.tests_total,
            detail=detail,
        )
