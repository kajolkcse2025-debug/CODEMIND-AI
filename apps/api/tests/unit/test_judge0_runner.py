
import httpx
import pytest

from app.integrations.code_runner.base import RunRequest, RunTestCase, Verdict
from app.integrations.code_runner.judge0 import Judge0Runner


def make_runner(mock_response):
    """Build a runner whose HTTP requests never leave this test."""
    client = httpx.Client(
        transport=httpx.MockTransport(mock_response)
    )
    runner = Judge0Runner(
        base_url="https://judge0.example.test/",
        client=client,
        poll_interval_sec=0,
        max_poll_attempts=2,
    )
    return runner, client


def make_request(expected="5\n"):
    return RunRequest(
        language="python",
        source_code="print(2 + 3)",
        test_cases=[
            RunTestCase(
                stdin="",
                expected_stdout=expected,
                tags=("basic-math",),
            )
        ],
    )


def test_accepted_solution():
    def handler(request):
        if request.method == "POST":
            return httpx.Response(201, json={"token": "test-token"})

        return httpx.Response(
            200,
            json={
                "status": {"id": 3, "description": "Accepted"},
                "stdout": "5\n",
                "time": "0.01",
                "memory": 1024,
            },
        )

    runner, client = make_runner(handler)
    try:
        result = runner.run(make_request())

        assert result.verdict is Verdict.ACCEPTED
        assert result.verified is True
        assert result.tests_passed == 1
        assert result.tests_total == 1
    finally:
        runner.close()
        client.close()


def test_wrong_answer():
    def handler(request):
        if request.method == "POST":
            return httpx.Response(201, json={"token": "wrong-token"})

        return httpx.Response(
            200,
            json={
                "status": {"id": 3, "description": "Accepted"},
                "stdout": "99\n",
            },
        )

    runner, client = make_runner(handler)
    try:
        result = runner.run(make_request(expected="5\n"))

        assert result.verdict is Verdict.WRONG_ANSWER
        assert result.verified is True
        assert result.tests_passed == 0
        assert result.failed_test_tags == ("basic-math",)
    finally:
        runner.close()
        client.close()


def test_runtime_error():
    def handler(request):
        if request.method == "POST":
            return httpx.Response(201, json={"token": "error-token"})

        return httpx.Response(
            200,
            json={
                "status": {
                    "id": 11,
                    "description": "Runtime Error (NZEC)",
                },
                "stderr": "Example runtime error",
            },
        )

    runner, client = make_runner(handler)
    try:
        result = runner.run(make_request())

        assert result.verdict is Verdict.RUNTIME_ERROR
        assert result.verified is True
        assert result.tests_passed == 0
    finally:
        runner.close()
        client.close()


def test_submission_that_never_finishes_is_unverified():
    def handler(request):
        if request.method == "POST":
            return httpx.Response(201, json={"token": "pending-token"})

        return httpx.Response(
            200,
            json={"status": {"id": 1, "description": "In Queue"}},
        )

    runner, client = make_runner(handler)
    try:
        result = runner.run(make_request())

        assert result.verdict is Verdict.RUNNER_UNAVAILABLE
        assert result.verified is False
        assert result.counts_toward_metrics is False
    finally:
        runner.close()
        client.close()

def test_http_failure_is_unverified():
    def handler(request):
        return httpx.Response(503, text="Service unavailable")

    runner, client = make_runner(handler)
    try:
        result = runner.run(make_request())

        assert result.verdict is Verdict.RUNNER_UNAVAILABLE
        assert result.verified is False
        assert result.counts_toward_metrics is False
    finally:
        runner.close()
        client.close()


def test_all_multiple_test_cases_pass():
    submission_count = 0

    def handler(request):
        nonlocal submission_count

        if request.method == "POST":
            submission_count += 1
            return httpx.Response(
                201,
                json={"token": f"token-{submission_count}"},
            )

        stdin = request.url.params.get("stdin", "")
        output = "8\n" if submission_count == 1 else "5\n"

        return httpx.Response(
            200,
            json={
                "status": {"id": 3, "description": "Accepted"},
                "stdout": output,
            },
        )

    request = RunRequest(
        language="python",
        source_code="print(2 + 3)",
        test_cases=[
            RunTestCase(stdin="3 5", expected_stdout="8\n", tags=("case-1",)),
            RunTestCase(stdin="-2 7", expected_stdout="5\n", tags=("case-2",)),
        ],
    )

    runner, client = make_runner(handler)
    try:
        result = runner.run(request)

        assert result.verdict is Verdict.ACCEPTED
        assert result.verified is True
        assert result.tests_passed == 2
        assert result.tests_total == 2
        assert submission_count == 2
    finally:
        runner.close()
        client.close()

@pytest.mark.parametrize(
    ("language", "expected_id"),
    [
        ("python", 100),
        ("java", 91),
        ("cpp", 105),
    ],
)
def test_submission_uses_correct_language_id(language, expected_id):
    captured_language_ids = []

    def handler(request):
        if request.method == "POST":
            import json

            payload = json.loads(request.content)
            captured_language_ids.append(payload["language_id"])
            return httpx.Response(
                201,
                json={"token": "language-test-token"},
            )

        return httpx.Response(
            200,
            json={
                "status": {"id": 3, "description": "Accepted"},
                "stdout": "5\n",
            },
        )

    runner, client = make_runner(handler)
    request = RunRequest(
        language=language,
        source_code="print(2 + 3)",
        test_cases=[
            RunTestCase(
                stdin="",
                expected_stdout="5\n",
                tags=("language-check",),
            )
        ],
    )

    try:
        result = runner.run(request)

        assert captured_language_ids == [expected_id]
        assert result.verdict is Verdict.ACCEPTED
        assert result.verified is True
    finally:
        runner.close()
        client.close()
