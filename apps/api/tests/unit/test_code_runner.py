from pathlib import Path

from app.integrations.code_runner import (
    FakeCodeRunner,
    RunRequest,
    RunResult,
    RunTestCase,
    Verdict,
    build_code_runner,
)


def test_fake_runner_reports_unavailable_and_unverified() -> None:
    request = RunRequest(
        language="python",
        source_code="print('hi')",
        test_cases=[RunTestCase("1", "1"), RunTestCase("2", "2")],
    )
    result = FakeCodeRunner().run(request)
    assert result.verdict is Verdict.RUNNER_UNAVAILABLE
    assert result.verified is False
    assert result.tests_total == 2
    assert result.tests_passed == 0
    assert result.counts_toward_metrics is False


def test_fake_runner_never_executes_submitted_code(tmp_path: Path) -> None:
    marker = tmp_path / "executed.txt"
    source = f"open({str(marker)!r}, 'w').write('ran')"
    FakeCodeRunner().run(RunRequest(language="python", source_code=source))
    assert not marker.exists()


def test_unverified_results_cannot_count_even_if_marked_accepted() -> None:
    result = RunResult(verdict=Verdict.ACCEPTED, verified=False, tests_passed=3, tests_total=3)
    assert result.counts_toward_metrics is False


def test_runner_unavailable_never_counts_even_if_marked_verified() -> None:
    result = RunResult(verdict=Verdict.RUNNER_UNAVAILABLE, verified=True)
    assert result.counts_toward_metrics is False


def test_verified_accepted_result_counts() -> None:
    assert RunResult(verdict=Verdict.ACCEPTED, verified=True).counts_toward_metrics is True


def test_factory_returns_the_fake_runner_in_phase_one() -> None:
    assert isinstance(build_code_runner(), FakeCodeRunner)
