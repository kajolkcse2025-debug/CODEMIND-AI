"""Regression tests for races found during the Phase 1 verification pass.

These use their own committing sessions (real concurrency needs real transactions) and clean up
after themselves, so they never leave data behind in the shared test database.
"""

import threading
import uuid
from collections import Counter
from types import SimpleNamespace

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.repositories.user import Identity, UserRepository
from app.schemas.profile import ProfileIn
from app.services.profile_service import ProfileService
from app.services.user_service import UserService
from tests.conftest import TEST_DATABASE_URL

pytestmark = pytest.mark.db


@pytest.fixture
def pool_engine(engine: Engine) -> Engine:  # depends on `engine` so migrations have run
    pooled = create_engine(TEST_DATABASE_URL, pool_size=24, max_overflow=0)
    yield pooled  # type: ignore[misc]
    pooled.dispose()


def _service(session: Session) -> ProfileService:
    return ProfileService(session, ProfileRepository(session), UserRepository(session))


def test_second_profile_create_that_passes_the_check_becomes_409_not_500(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = User(firebase_uid=f"race-{uuid.uuid4()}")
    db_session.add(user)
    db_session.flush()
    _service(db_session).create(user, ProfileIn(name="First"))
    # The losing request of a double-submit has already passed the "no profile yet" check.
    monkeypatch.setattr(ProfileRepository, "get", lambda self, user_id: None)
    with pytest.raises(ConflictError) as info:
        _service(db_session).create(user, ProfileIn(name="Second"))
    assert info.value.code == "profile_exists"


def test_other_integrity_errors_are_not_mislabelled_as_profile_exists(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = User(firebase_uid=f"race-{uuid.uuid4()}")
    db_session.add(user)
    db_session.flush()
    orig = SimpleNamespace(diag=SimpleNamespace(constraint_name="ck_profiles_cgpa_in_scale"))

    def explode(self: ProfileRepository, user_id: uuid.UUID, values: dict[str, object]) -> None:
        raise IntegrityError("INSERT ...", {}, orig)  # type: ignore[arg-type]

    monkeypatch.setattr(ProfileRepository, "create", explode)
    with pytest.raises(IntegrityError):
        _service(db_session).create(user, ProfileIn(name="X"))


def test_concurrent_profile_creation_over_http_never_returns_500(client, verifier) -> None:  # type: ignore[no-untyped-def]
    headers = verifier.add(f"http-race-{uuid.uuid4()}", "race@example.com")
    assert client.post("/api/v1/profile", json={"name": "A"}, headers=headers).status_code == 201
    from app.repositories import profile as profile_module

    original = profile_module.ProfileRepository.get
    profile_module.ProfileRepository.get = lambda self, user_id: None  # type: ignore[method-assign]
    try:
        response = client.post("/api/v1/profile", json={"name": "B"}, headers=headers)
    finally:
        profile_module.ProfileRepository.get = original  # type: ignore[method-assign]
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "profile_exists"


def test_skill_updates_in_opposite_order_do_not_deadlock(pool_engine: Engine) -> None:
    """Unfixed code failed ~8% of these with PostgreSQL DeadlockDetected (40P01)."""
    names = [f"ConcSkill{i}" for i in range(12)]
    tag = uuid.uuid4().hex[:8]
    outcomes: Counter[str] = Counter()
    created: list[uuid.UUID] = []

    def worker(user_id: uuid.UUID, order: list[str], barrier: threading.Barrier) -> None:
        session = Session(pool_engine)
        try:
            barrier.wait()
            ProfileRepository(session).replace_skills(user_id, order)
            session.commit()
            outcomes["ok"] += 1
        except Exception as exc:
            session.rollback()
            outcomes[type(getattr(exc, "orig", exc)).__name__] += 1
        finally:
            session.close()

    try:
        for round_no in range(12):
            with Session(pool_engine) as session:
                users = [User(firebase_uid=f"dl-{tag}-{round_no}-{i}") for i in range(16)]
                session.add_all(users)
                session.commit()
                ids = [u.id for u in users]
            created.extend(ids)
            barrier = threading.Barrier(16)
            threads = [
                threading.Thread(
                    target=worker, args=(ids[i], names if i % 2 == 0 else names[::-1], barrier)
                )
                for i in range(16)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
    finally:
        with pool_engine.begin() as conn:
            conn.execute(text("DELETE FROM users WHERE firebase_uid LIKE :p"), {"p": f"dl-{tag}-%"})
            conn.execute(text("DELETE FROM skills WHERE slug LIKE 'concskill%'"))
    assert dict(outcomes) == {"ok": 12 * 16}


def test_skill_replacement_keeps_first_seen_name_and_dedupes(db_session: Session) -> None:
    user = User(firebase_uid=f"sk-{uuid.uuid4()}")
    db_session.add(user)
    db_session.flush()
    repo = ProfileRepository(db_session)
    repo.replace_skills(user.id, ["Python", "python", "C++"])
    assert repo.skill_names(user.id) == ["C++", "Python"]
    repo.replace_skills(user.id, [])
    assert repo.skill_names(user.id) == []


def test_concurrent_first_requests_provision_exactly_one_user(pool_engine: Engine) -> None:
    uid = f"first-{uuid.uuid4()}"
    results: list[uuid.UUID] = []
    errors: list[Exception] = []
    barrier = threading.Barrier(16)

    def worker() -> None:
        session = Session(pool_engine, expire_on_commit=False)
        try:
            barrier.wait()
            user = UserService(session, UserRepository(session)).provision(
                Identity(uid, f"{uid}@example.com", "Same Person")
            )
            results.append(user.id)
        except Exception as exc:
            errors.append(exc)
        finally:
            session.close()

    try:
        threads = [threading.Thread(target=worker) for _ in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    finally:
        with pool_engine.begin() as conn:
            conn.execute(text("DELETE FROM users WHERE firebase_uid = :u"), {"u": uid})
    assert errors == []
    assert len(set(results)) == 1 and len(results) == 16
