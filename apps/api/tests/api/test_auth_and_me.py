import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from tests.conftest import FakeTokenVerifier

pytestmark = pytest.mark.db


def test_me_requires_a_token(client: TestClient) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    error = response.json()["error"]
    assert error["code"] == "unauthenticated"
    assert error["details"]["reason"] == "missing_token"


def test_me_rejects_a_token_the_verifier_does_not_accept(client: TestClient) -> None:
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer forged"})
    assert response.status_code == 401
    assert response.json()["error"]["details"]["reason"] == "token_invalid"


def test_me_rejects_non_bearer_schemes(client: TestClient) -> None:
    response = client.get("/api/v1/me", headers={"Authorization": "Basic abc"})
    assert response.status_code == 401


def test_expired_token_reports_reason(client: TestClient, verifier: FakeTokenVerifier) -> None:
    verifier.errors["old"] = "token_expired"
    response = client.get("/api/v1/me", headers={"Authorization": "Bearer old"})
    assert response.status_code == 401
    assert response.json()["error"]["details"]["reason"] == "token_expired"


def test_me_provisions_user_from_verified_token(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    headers = verifier.add("uid-1", "asha@example.com", name="Asha K", email_verified=False)
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "asha@example.com"
    assert body["user"]["display_name"] == "Asha K"
    assert body["user"]["role"] == "student"
    assert body["user"]["onboarding_status"] == "not_started"
    assert body["profile"] is None
    assert body["flags"] == {"email_verified": False}


def test_repeated_calls_return_the_same_user_without_duplicates(
    client: TestClient, verifier: FakeTokenVerifier, db_session: Session
) -> None:
    headers = verifier.add("uid-2", "same@example.com")
    first = client.get("/api/v1/me", headers=headers).json()["user"]["id"]
    second = client.get("/api/v1/me", headers=headers).json()["user"]["id"]
    assert first == second
    count = db_session.scalar(
        select(func.count()).select_from(User).where(User.firebase_uid == "uid-2")
    )
    assert count == 1


def test_different_tokens_are_different_users(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    a = client.get("/api/v1/me", headers=verifier.add("uid-a", "a@example.com")).json()
    b = client.get("/api/v1/me", headers=verifier.add("uid-b", "b@example.com")).json()
    assert a["user"]["id"] != b["user"]["id"]


def test_client_supplied_identity_is_ignored(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    victim = client.get("/api/v1/me", headers=verifier.add("victim", "victim@example.com")).json()
    headers = {
        **verifier.add("attacker", "attacker@example.com"),
        "X-User-Id": victim["user"]["id"],
    }
    response = client.get(f"/api/v1/me?user_id={victim['user']['id']}", headers=headers)
    assert response.json()["user"]["id"] != victim["user"]["id"]
    assert response.json()["user"]["email"] == "attacker@example.com"


def test_pending_deletion_accounts_are_blocked(
    client: TestClient, verifier: FakeTokenVerifier, db_session: Session
) -> None:
    headers = verifier.add("uid-del", "del@example.com")
    client.get("/api/v1/me", headers=headers)
    user = db_session.scalars(select(User).where(User.firebase_uid == "uid-del")).one()
    user.account_status = "pending_deletion"
    db_session.flush()
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "account_pending_deletion"


def test_email_is_updated_but_never_erased_by_a_token_without_one(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    client.get("/api/v1/me", headers=verifier.add("uid-e", "first@example.com"))
    headers = verifier.add("uid-e", None)
    assert client.get("/api/v1/me", headers=headers).json()["user"]["email"] == "first@example.com"
    headers = verifier.add("uid-e", "second@example.com")
    assert client.get("/api/v1/me", headers=headers).json()["user"]["email"] == "second@example.com"


def test_duplicate_email_across_accounts_is_a_clean_conflict(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    client.get("/api/v1/me", headers=verifier.add("uid-x", "dup@example.com"))
    response = client.get("/api/v1/me", headers=verifier.add("uid-y", "DUP@example.com"))
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_in_use"
