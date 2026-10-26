"""Database foundation: migrations match the models, constraints hold, seeds are idempotent."""

import uuid
from decimal import Decimal

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.db.base import Base
from app.models.activity import CodeSubmission, CodingAttempt
from app.models.content import Problem, ProblemTopic, Topic
from app.models.intelligence import CodingDnaTrait
from app.models.user import User
from app.seeds.topics import CANONICAL_TOPICS, seed_topics

pytestmark = pytest.mark.db

EXPECTED_TABLES = {
    "users", "profiles", "topics", "skills", "user_skills", "problems", "problem_topics",
    "coding_attempts", "code_submissions", "detected_errors", "detected_weaknesses",
    "topic_performance", "coding_dna", "roadmaps", "roadmap_items", "daily_missions",
    "mission_items", "interview_sessions", "interview_questions", "interview_responses",
    "interview_scores", "achievements", "user_achievements", "streaks", "ai_conversations",
    "problem_test_cases",
}  # fmt: skip


def test_migrated_database_has_exactly_the_expected_tables(engine: Engine) -> None:
    tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
    assert tables == EXPECTED_TABLES
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_models_and_migrations_have_not_drifted(engine: Engine) -> None:
    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection, opts={"compare_type": True, "compare_server_default": True}
        )
        assert compare_metadata(context, Base.metadata) == []


def test_every_user_owned_table_has_an_indexed_user_id(engine: Engine) -> None:
    inspector = inspect(engine)
    missing = []
    for table in sorted(EXPECTED_TABLES):
        columns = {c["name"] for c in inspector.get_columns(table)}
        if "user_id" not in columns or table in (
            "profiles",
            "streaks",
            "coding_dna",
            "user_skills",
        ):
            continue
        leading = [
            ix["column_names"][0] for ix in inspector.get_indexes(table) if ix["column_names"]
        ]
        leading += [uq["column_names"][0] for uq in inspector.get_unique_constraints(table)]
        if "user_id" not in leading:
            missing.append(table)
    assert missing == []


def _user(session: Session, suffix: str = "") -> User:
    user = User(firebase_uid=f"uid-{uuid.uuid4()}{suffix}", email=None)
    session.add(user)
    session.flush()
    return user


def test_users_email_is_unique_case_insensitively(db_session: Session) -> None:
    db_session.add(User(firebase_uid="a", email="Same@Example.com"))
    db_session.flush()
    db_session.add(User(firebase_uid="b", email="same@example.com"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_users_may_have_no_email(db_session: Session) -> None:
    db_session.add_all([User(firebase_uid="n1"), User(firebase_uid="n2")])
    db_session.flush()


def test_calibrating_dna_trait_cannot_carry_a_score(db_session: Session) -> None:
    user = _user(db_session)
    db_session.add(
        CodingDnaTrait(user_id=user.id, trait="debugging", state="calibrating", score=Decimal("50"))
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_dna_trait_names_are_constrained(db_session: Session) -> None:
    user = _user(db_session)
    db_session.add(CodingDnaTrait(user_id=user.id, trait="made_up_trait"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def _problem(session: Session) -> Problem:
    problem = Problem(
        slug=f"p-{uuid.uuid4()}",
        title="t",
        statement_md="s",
        difficulty="easy",
        expected_time_sec=600,
    )
    session.add(problem)
    session.flush()
    return problem


def _attempt(session: Session, user: User, problem: Problem) -> CodingAttempt:
    attempt = CodingAttempt(
        user_id=user.id, problem_id=problem.id, problem_version=1, context="practice"
    )
    session.add(attempt)
    session.flush()
    return attempt


def test_runner_unavailable_submission_can_never_be_marked_verified(db_session: Session) -> None:
    user = _user(db_session)
    attempt = _attempt(db_session, user, _problem(db_session))
    db_session.add(
        CodeSubmission(
            attempt_id=attempt.id,
            user_id=user.id,
            language="python",
            code="x",
            code_sha256="0" * 64,
            kind="submit",
            verdict="runner_unavailable",
            verified=True,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_submissions_default_to_unverified(db_session: Session) -> None:
    user = _user(db_session)
    attempt = _attempt(db_session, user, _problem(db_session))
    submission = CodeSubmission(
        attempt_id=attempt.id,
        user_id=user.id,
        language="python",
        code="x",
        code_sha256="0" * 64,
        kind="run",
        verdict="runner_unavailable",
    )
    db_session.add(submission)
    db_session.flush()
    db_session.refresh(submission)
    assert submission.verified is False


def test_submission_code_size_is_capped(db_session: Session) -> None:
    user = _user(db_session)
    attempt = _attempt(db_session, user, _problem(db_session))
    db_session.add(
        CodeSubmission(
            attempt_id=attempt.id,
            user_id=user.id,
            language="python",
            code="x" * 65537,
            code_sha256="0" * 64,
            kind="submit",
            verdict="accepted",
            verified=True,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_problem_has_at_most_one_primary_topic(db_session: Session) -> None:
    seed_topics(db_session)
    problem = _problem(db_session)
    db_session.add(ProblemTopic(problem_id=problem.id, topic_id=1, is_primary=True))
    db_session.flush()
    db_session.add(ProblemTopic(problem_id=problem.id, topic_id=2, is_primary=True))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_deleting_a_user_cascades_to_owned_rows(db_session: Session) -> None:
    user = _user(db_session)
    attempt = _attempt(db_session, user, _problem(db_session))
    db_session.execute(text("DELETE FROM users WHERE id = :id"), {"id": user.id})
    remaining = db_session.execute(
        text("SELECT count(*) FROM coding_attempts WHERE id = :id"), {"id": attempt.id}
    ).scalar_one()
    assert remaining == 0


def test_canonical_topics_seed_is_complete_and_idempotent(db_session: Session) -> None:
    assert seed_topics(db_session) == 17
    assert seed_topics(db_session) == 17
    topics = list(db_session.scalars(select(Topic).order_by(Topic.display_order)))
    assert [t.slug for t in topics] == [t.slug for t in CANONICAL_TOPICS]
    assert len({t.slug for t in topics}) == 17
    assert [t.display_order for t in topics] == list(range(1, 18))


def test_diagnostic_rounds_follow_the_blueprint(db_session: Session) -> None:
    seed_topics(db_session)
    by_round: dict[int | None, set[str]] = {}
    for topic in db_session.scalars(select(Topic)):
        by_round.setdefault(topic.diagnostic_round, set()).add(topic.slug)
    assert by_round[1] == {"arrays", "strings", "hashing"}
    assert by_round[2] == {"sliding-window", "stack", "queue"}
    assert by_round[3] == {"trees", "graphs", "dynamic-programming"}
    assert len(by_round[None]) == 8


def test_reseeding_never_overwrites_a_tuned_interview_weight(db_session: Session) -> None:
    seed_topics(db_session)
    topic = db_session.scalars(select(Topic).where(Topic.slug == "graphs")).one()
    assert topic.interview_weight == Decimal("1.00")
    topic.interview_weight = Decimal("1.40")
    db_session.flush()
    seed_topics(db_session)
    db_session.refresh(topic)
    assert topic.interview_weight == Decimal("1.40")
