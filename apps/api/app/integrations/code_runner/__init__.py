from app.integrations.code_runner.base import (
    CodeRunner,
    RunRequest,
    RunResult,
    RunTestCase,
    Verdict,
)
from app.integrations.code_runner.fake import FakeCodeRunner


def build_code_runner() -> CodeRunner:
    """Use Judge0 when configured; otherwise use the safe fake runner."""
    from app.config import get_settings

    settings = get_settings()

    if settings.judge0_base_url:
        from app.integrations.code_runner.judge0 import build_judge0_runner

        return build_judge0_runner()

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
