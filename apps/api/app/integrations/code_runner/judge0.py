
"""Judge0 integration for safely executing student code."""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.config import get_settings
from app.integrations.code_runner.base import (
    RunRequest,
    RunResult,
    Verdict,
)


_LANGUAGE_IDS = {
    "python": 100,
    "python3": 100,
    "java": 91,
    "cpp": 105,
    "c++": 105,
    "c": 105,
    "javascript": 63,
    "js": 63,
}


class Judge0Runner:
    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        timeout_sec: int = 60,
        client: httpx.Client | None = None,
        poll_interval_sec: float = 0.5,
        max_poll_attempts: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.api_key = api_key
        self.timeout_sec = timeout_sec
        self.client = client
        self.poll_interval_sec = poll_interval_sec
        self.max_poll_attempts = max_poll_attempts
    def close(self) -> None:
        """Close the HTTP client if it is still open."""
        if self.client is not None:
            self.client.close()
            self.client = None
    

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key

        return headers

    def _submit(
        self,
        client: httpx.Client,
        language_id: int,
        source_code: str,
        stdin: str,
        request: RunRequest,
    ) -> str:
        response = client.post(
            f"{self.base_url}submissions",
            params={
                "base64_encoded": "false",
                "wait": "false",
            },
            headers=self._headers(),
            json={
                "language_id": language_id,
                "source_code": source_code,
                "stdin": stdin,
                "cpu_time_limit": request.time_limit_ms / 1000,
                "memory_limit": request.memory_limit_kb,
            },
        )
        response.raise_for_status()

        token = response.json().get("token")
        if not token:
            raise ValueError("Judge0 did not return a submission token.")

        return token

    def _poll(
        self,
        client: httpx.Client,
        token: str,
    ) -> dict[str, Any]:
        for _ in range(self.max_poll_attempts):
            response = client.get(
                f"{self.base_url}submissions/{token}",
                params={"base64_encoded": "false"},
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()

            status = data.get("status") or {}
            status_id = status.get("id")

            if status_id not in (1, 2):
                return data

            time.sleep(self.poll_interval_sec)

        raise TimeoutError("Timed out waiting for Judge0.")

    @staticmethod
    def _verdict(data: dict[str, Any]) -> Verdict:
        status = (data.get("status") or {}).get("id")
        description = (
            (data.get("status") or {}).get("description") or ""
        ).strip().lower()

        stderr = (data.get("stderr") or "").lower()
        compile_output = (data.get("compile_output") or "").lower()
        error_output = stderr + "\n" + compile_output

        if status == 3 or description == "accepted":
            return Verdict.ACCEPTED

        if status == 4 or "wrong answer" in description:
            return Verdict.WRONG_ANSWER

        if status == 5 or "time limit" in description:
            return Verdict.TIME_LIMIT

        if status == 6 or "compilation error" in description:
            return Verdict.COMPILE_ERROR

        # Judge0 may report Python syntax errors as Runtime Error (NZEC).
        if status == 11 and (
            "syntaxerror:" in error_output
            or "indentationerror:" in error_output
        ):
            return Verdict.COMPILE_ERROR

        if status in (7, 8, 9, 10, 11, 12, 14):
            return Verdict.RUNTIME_ERROR

        if status == 13 or "internal error" in description:
            return Verdict.RUNNER_UNAVAILABLE

        return Verdict.RUNNER_UNAVAILABLE

    @staticmethod
    def _normalise_output(value: str | None) -> str:
        return (value or "").strip()

    def run(self, request: RunRequest) -> RunResult:
        language = request.language.strip().lower()
        language_id = _LANGUAGE_IDS.get(language)

        if language_id is None:
            return RunResult(
                verdict=Verdict.RUNNER_UNAVAILABLE,
                verified=False,
                tests_passed=0,
                tests_total=len(request.test_cases),
                detail=f"Unsupported language: {request.language}",
            )

        if not request.test_cases:
            return RunResult(
                verdict=Verdict.RUNNER_UNAVAILABLE,
                verified=False,
                tests_passed=0,
                tests_total=0,
                detail="No test cases are configured for this problem.",
            )

        tests_passed = 0
        failed_test_tags: list[str] = []
        max_time_ms: int | None = None
        max_memory_kb: int | None = None

        client = self.client or httpx.Client(timeout=self.timeout_sec)

        try:
            for index, test_case in enumerate(
                request.test_cases,
                start=1,
            ):
                token = self._submit(
                    client=client,
                    language_id=language_id,
                    source_code=request.source_code,
                    stdin=test_case.stdin,
                    request=request,
                )

                data = self._poll(client, token)
                verdict = self._verdict(data)

                time_value = data.get("time")
                if time_value is not None:
                    elapsed_ms = int(float(time_value) * 1000)
                    max_time_ms = (
                        elapsed_ms
                        if max_time_ms is None
                        else max(max_time_ms, elapsed_ms)
                    )

                memory_value = data.get("memory")
                if memory_value is not None:
                    memory_kb = int(memory_value)
                    max_memory_kb = (
                        memory_kb
                        if max_memory_kb is None
                        else max(max_memory_kb, memory_kb)
                    )

                if verdict == Verdict.RUNNER_UNAVAILABLE:
                    return RunResult(
                        verdict=verdict,
                        verified=False,
                        tests_passed=tests_passed,
                        tests_total=len(request.test_cases),
                        failed_test_tags=tuple(failed_test_tags),
                        max_time_ms=max_time_ms,
                        max_memory_kb=max_memory_kb,
                        detail="Judge0 could not complete the submission.",
                    )

                if verdict != Verdict.ACCEPTED:
                    if test_case.tags:
                        failed_test_tags.extend(test_case.tags)
                    else:
                        failed_test_tags.append(f"test_{index}")

                    return RunResult(
                        verdict=verdict,
                        verified=True,
                        tests_passed=tests_passed,
                        tests_total=len(request.test_cases),
                        failed_test_tags=tuple(failed_test_tags),
                        max_time_ms=max_time_ms,
                        max_memory_kb=max_memory_kb,
                        detail=(
                            "Your code could not complete successfully. "
                            "Check your code and try again."
                            if verdict
                            in (
                                Verdict.RUNTIME_ERROR,
                                Verdict.COMPILE_ERROR,
                                Verdict.TIME_LIMIT,
                                Verdict.MEMORY_LIMIT,
                            )
                            else "Some tests did not pass. "
                            "Review your code and try again."
                        ),
                    )

                actual = self._normalise_output(data.get("stdout"))
                expected = self._normalise_output(
                    test_case.expected_stdout
                )

                if actual != expected:
                    if test_case.tags:
                        failed_test_tags.extend(test_case.tags)
                    else:
                        failed_test_tags.append(f"test_{index}")

                    return RunResult(
                        verdict=Verdict.WRONG_ANSWER,
                        verified=True,
                        tests_passed=tests_passed,
                        tests_total=len(request.test_cases),
                        failed_test_tags=tuple(failed_test_tags),
                        max_time_ms=max_time_ms,
                        max_memory_kb=max_memory_kb,
                        detail=(
                            "Some tests did not pass. "
                            "Review your code and try again."
                        ),
                    )

                tests_passed += 1

        except (
            httpx.HTTPError,
            ValueError,
            KeyError,
            TypeError,
            TimeoutError,
        ):
            return RunResult(
                verdict=Verdict.RUNNER_UNAVAILABLE,
                verified=False,
                tests_passed=tests_passed,
                tests_total=len(request.test_cases),
                failed_test_tags=tuple(failed_test_tags),
                max_time_ms=max_time_ms,
                max_memory_kb=max_memory_kb,
                detail=(
                    "The code execution service is temporarily unavailable."
                ),
            )
        finally:
            # Only close clients created by this runner.
            if self.client is None:
                client.close()

        return RunResult(
            verdict=Verdict.ACCEPTED,
            verified=True,
            tests_passed=tests_passed,
            tests_total=len(request.test_cases),
            failed_test_tags=(),
            max_time_ms=max_time_ms,
            max_memory_kb=max_memory_kb,
            detail="All tests passed.",
        )


def build_judge0_runner() -> Judge0Runner:
    settings = get_settings()

    return Judge0Runner(
        base_url=settings.judge0_base_url,
        api_key=getattr(settings, "judge0_api_key", ""),
        timeout_sec=getattr(settings, "judge0_timeout_sec", 60),
    )
