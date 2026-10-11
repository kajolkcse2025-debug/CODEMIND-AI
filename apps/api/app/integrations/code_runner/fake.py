from app.integrations.code_runner.base import RunRequest, RunResult, Verdict


class FakeCodeRunner:
    """Stand-in until Judge0 is integrated. Executes nothing; always reports unavailable.

    The result is explicitly unverified, so it can never affect mastery, XP, DNA or readiness.
    """

    def run(self, request: RunRequest) -> RunResult:
        return RunResult(
            verdict=Verdict.RUNNER_UNAVAILABLE,
            verified=False,
            tests_total=len(request.test_cases),
            detail="No code runner is configured. Nothing was executed.",
        )
