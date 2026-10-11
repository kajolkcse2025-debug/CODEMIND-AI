from app.integrations.code_runner.base import (
    CodeRunner,
    RunRequest,
    RunResult,
    RunTestCase,
    Verdict,
)
from app.integrations.code_runner.fake import FakeCodeRunner


def build_code_runner() -> CodeRunner:
    """Phase 1 has only the fake runner. Judge0 replaces it behind this same factory."""
    return FakeCodeRunner()


__all__ = [
    "CodeRunner",
    "FakeCodeRunner",
    "RunRequest",
    "RunResult",
    "RunTestCase",
    "Verdict",
    "build_code_runner",
]
