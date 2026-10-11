"""The code-execution seam.

Student code must NEVER run inside the FastAPI process. Production execution will go
FastAPI -> CodeRunner -> sandboxed runner (Judge0). A result only counts toward mastery,
XP, Coding DNA or readiness when ``verified`` is True.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class Verdict(StrEnum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT = "time_limit"
    MEMORY_LIMIT = "memory_limit"
    COMPILE_ERROR = "compile_error"
    RUNNER_UNAVAILABLE = "runner_unavailable"


@dataclass(frozen=True)
class RunTestCase:
    stdin: str
    expected_stdout: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunRequest:
    language: str
    source_code: str
    test_cases: Sequence[RunTestCase] = ()
    time_limit_ms: int = 2000
    memory_limit_kb: int = 262144


@dataclass(frozen=True)
class RunResult:
    verdict: Verdict
    verified: bool
    tests_passed: int = 0
    tests_total: int = 0
    failed_test_tags: tuple[str, ...] = field(default_factory=tuple)
    max_time_ms: int | None = None
    max_memory_kb: int | None = None
    detail: str | None = None

    @property
    def counts_toward_metrics(self) -> bool:
        """False for anything unverified. Mastery, XP, DNA and readiness must check this."""
        return self.verified and self.verdict is not Verdict.RUNNER_UNAVAILABLE


class CodeRunner(Protocol):
    def run(self, request: RunRequest) -> RunResult: ...
