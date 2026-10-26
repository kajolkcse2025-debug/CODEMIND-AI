
from typing import Literal

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    language: Literal["python", "java", "cpp"]
    source_code: str = Field(min_length=1, max_length=50000)


class SubmissionResult(BaseModel):
    verdict: Literal[
        "accepted",
        "wrong_answer",
        "runtime_error",
        "time_limit",
        "memory_limit",
        "compile_error",
        "runner_unavailable",
    ]
    verified: bool
    tests_passed: int = Field(ge=0)
    tests_total: int = Field(ge=0)
    detail: str | None = None
