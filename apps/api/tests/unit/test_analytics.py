import ast
from datetime import UTC, datetime
from pathlib import Path

import app.analytics as analytics
from app.analytics import (
    DNA_TRAITS,
    WEAKNESS_CODES,
    AttemptFact,
    ComponentScore,
    MetricState,
    SubmissionFact,
    calculate_coding_dna,
    calculate_readiness,
    calculate_topic_mastery,
    detect_weaknesses,
    verified_only,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def attempt(attempt_id: str, *, verified: bool, outcome: str = "accepted") -> AttemptFact:
    return AttemptFact(
        attempt_id=attempt_id,
        topic_slug="arrays",
        difficulty="easy",
        outcome=outcome,  # type: ignore[arg-type]
        verified=verified,
    )


def test_public_api_imports() -> None:
    for name in analytics.__all__:
        assert hasattr(analytics, name)


def test_mastery_without_evidence_is_unavailable_not_zero() -> None:
    result = calculate_topic_mastery("arrays", [], now=NOW)
    assert result.score is None
    assert result.state is MetricState.UNAVAILABLE
    assert result.evidence_count == 0
    assert result.reason == "no_verified_evidence"


def test_unverified_attempts_never_count_as_evidence() -> None:
    attempts = [attempt("a", verified=False), attempt("b", verified=False)]
    result = calculate_topic_mastery("arrays", attempts, now=NOW)
    assert result.evidence_count == 0


def test_verified_attempts_count_but_phase_one_still_returns_no_score() -> None:
    attempts = [attempt("a", verified=True), attempt("b", verified=False)]
    result = calculate_topic_mastery("arrays", attempts, now=NOW)
    assert result.evidence_count == 1
    assert result.score is None  # no formula is implemented yet, so no number is invented
    assert result.reason == "scoring_not_implemented"


def test_in_progress_attempts_are_excluded() -> None:
    assert verified_only([attempt("a", verified=True, outcome="in_progress")]) == []


def test_coding_dna_has_every_trait_and_no_scores() -> None:
    dna = calculate_coding_dna([attempt("a", verified=True)], now=NOW)
    assert tuple(t.trait for t in dna.traits) == DNA_TRAITS
    assert all(t.score is None and t.state is MetricState.UNAVAILABLE for t in dna.traits)


def test_weakness_detection_never_invents_weaknesses() -> None:
    submissions = [
        SubmissionFact(
            "s1", "arrays", "wrong_answer", verified=True, failed_test_tags=("boundary",)
        )
    ]
    assert detect_weaknesses(submissions) == []
    assert len(WEAKNESS_CODES) == 10


def test_readiness_is_unavailable_and_never_a_probability() -> None:
    result = calculate_readiness({"dsa": ComponentScore(score=0.9, confidence=1.0)})
    assert result.score is None
    assert result.score_range is None
    assert result.provisional is True
    assert result.state is MetricState.UNAVAILABLE


def test_trait_vocabulary_matches_database_constraint() -> None:
    from app.models.intelligence import DNA_TRAITS as DB_TRAITS

    assert DB_TRAITS == DNA_TRAITS


FORBIDDEN_IMPORT_ROOTS = {
    "fastapi",
    "starlette",
    "sqlalchemy",
    "alembic",
    "psycopg",
    "redis",
    "httpx",
    "requests",
    "firebase_admin",
    "google",
    "socket",
    "urllib",
    "subprocess",
}
FORBIDDEN_APP_PREFIXES = (
    "app.db",
    "app.models",
    "app.repositories",
    "app.services",
    "app.api",
    "app.ai",
    "app.integrations",
    "app.core",
)


def _imports(path: Path) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_analytics_package_is_pure() -> None:
    """Architecture rule: no database, network, framework or AI imports in analytics."""
    package = Path(analytics.__file__).parent
    violations: list[str] = []
    for file in package.glob("*.py"):
        for module in _imports(file):
            root = module.split(".")[0]
            if root in FORBIDDEN_IMPORT_ROOTS or module.startswith(FORBIDDEN_APP_PREFIXES):
                violations.append(f"{file.name} imports {module}")
    assert violations == []
