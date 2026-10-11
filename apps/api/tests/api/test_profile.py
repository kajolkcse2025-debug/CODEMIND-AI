from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FakeTokenVerifier

pytestmark = pytest.mark.db

FULL: dict[str, Any] = {
    "name": "Asha K",
    "college": "IIT Madras",
    "degree": "B.Tech CSE",
    "current_year": 3,
    "cgpa": 8.75,
    "cgpa_scale": 10,
    "skills": ["Python", "C++", "React"],
    "dream_company": "Google",
    "dream_role": "SWE Intern",
    "target_package_lpa": 32.5,
    "github_username": "octocat",
    "linkedin_url": "https://www.linkedin.com/in/asha-k",
    "leetcode_username": "asha_k",
    "codeforces_username": "asha.k",
    "timezone": "Asia/Kolkata",
    "daily_minutes": 90,
    "preferred_language": "python",
}


@pytest.fixture
def headers(verifier: FakeTokenVerifier) -> dict[str, str]:
    return verifier.add("profile-user", "profile@example.com")


def test_profile_endpoints_require_auth(client: TestClient) -> None:
    assert client.get("/api/v1/profile").status_code == 401
    assert client.post("/api/v1/profile", json=FULL).status_code == 401
    assert client.put("/api/v1/profile", json=FULL).status_code == 401


def test_get_before_create_is_404_with_clear_code(
    client: TestClient, headers: dict[str, str]
) -> None:
    response = client.get("/api/v1/profile", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"


def test_create_then_read_round_trip(client: TestClient, headers: dict[str, str]) -> None:
    created = client.post("/api/v1/profile", json=FULL, headers=headers)
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Asha K"
    assert body["cgpa"] == 8.75
    assert body["target_package_lpa"] == 32.5
    assert body["skills"] == ["C++", "Python", "React"]  # catalogue order, not input order
    assert body["timezone"] == "Asia/Kolkata"
    assert client.get("/api/v1/profile", headers=headers).json() == body


def test_creating_a_profile_completes_onboarding_and_shows_in_me(
    client: TestClient, headers: dict[str, str]
) -> None:
    client.post("/api/v1/profile", json={"name": "Asha"}, headers=headers)
    me = client.get("/api/v1/me", headers=headers).json()
    assert me["user"]["onboarding_status"] == "complete"
    assert me["profile"]["name"] == "Asha"


def test_minimal_profile_uses_documented_defaults(
    client: TestClient, headers: dict[str, str]
) -> None:
    body = client.post("/api/v1/profile", json={"name": "Asha"}, headers=headers).json()
    assert body["timezone"] == "UTC"
    assert body["cgpa_scale"] == 10
    assert body["skills"] == []
    assert body["daily_minutes"] is None


def test_second_post_conflicts(client: TestClient, headers: dict[str, str]) -> None:
    client.post("/api/v1/profile", json=FULL, headers=headers)
    response = client.post("/api/v1/profile", json=FULL, headers=headers)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "profile_exists"


def test_put_before_create_is_404(client: TestClient, headers: dict[str, str]) -> None:
    response = client.put("/api/v1/profile", json=FULL, headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "profile_not_found"


def test_put_replaces_editable_fields_including_skills(
    client: TestClient, headers: dict[str, str]
) -> None:
    client.post("/api/v1/profile", json=FULL, headers=headers)
    updated = client.put(
        "/api/v1/profile",
        json={"name": "Asha Kumar", "skills": ["Rust"], "daily_minutes": 120},
        headers=headers,
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["name"] == "Asha Kumar"
    assert body["skills"] == ["Rust"]
    assert body["daily_minutes"] == 120
    assert body["college"] is None  # PUT is a full replacement; omitted optional fields reset


def test_invalid_input_returns_field_level_errors(
    client: TestClient, headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/profile",
        json={"name": "", "cgpa": 11, "timezone": "Mars/Base", "daily_minutes": 5},
        headers=headers,
    )
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {item["field"] for item in error["details"]["errors"]}
    assert {"name", "timezone", "daily_minutes"} <= fields
    assert error["request_id"] == response.headers["x-request-id"]


def test_cgpa_above_scale_is_rejected(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/profile", json={"name": "Asha", "cgpa": 4.5, "cgpa_scale": 4}, headers=headers
    )
    assert response.status_code == 422


def test_user_id_in_body_is_rejected(client: TestClient, headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/profile",
        json={"name": "Asha", "user_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )
    assert response.status_code == 422


def test_profiles_are_isolated_between_users(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    a = verifier.add("iso-a", "a@example.com")
    b = verifier.add("iso-b", "b@example.com")
    client.post("/api/v1/profile", json={"name": "Alice", "skills": ["Go"]}, headers=a)
    assert client.get("/api/v1/profile", headers=b).status_code == 404
    client.post("/api/v1/profile", json={"name": "Bob", "skills": ["Java"]}, headers=b)
    assert client.get("/api/v1/profile", headers=a).json()["name"] == "Alice"
    assert client.get("/api/v1/profile", headers=a).json()["skills"] == ["Go"]
    assert client.get("/api/v1/profile", headers=b).json()["skills"] == ["Java"]


def test_shared_skill_catalogue_entries_are_reused(
    client: TestClient, verifier: FakeTokenVerifier
) -> None:
    a = verifier.add("sk-a", "ska@example.com")
    b = verifier.add("sk-b", "skb@example.com")
    client.post("/api/v1/profile", json={"name": "A", "skills": ["Python"]}, headers=a)
    response = client.post(
        "/api/v1/profile", json={"name": "B", "skills": ["python", "SQL"]}, headers=b
    )
    assert response.status_code == 201
    assert response.json()["skills"] == ["Python", "SQL"]  # first-seen display name wins


def test_validation_error_for_unauthenticated_request_is_401_not_422(client: TestClient) -> None:
    response = client.post("/api/v1/profile", json={"name": ""})
    assert response.status_code == 401
