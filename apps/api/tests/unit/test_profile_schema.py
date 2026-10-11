from typing import Any

import pytest
from pydantic import ValidationError

from app.schemas.profile import ProfileIn


def valid(**overrides: Any) -> dict[str, Any]:
    return {"name": "Asha", **overrides}


def test_minimal_profile_is_valid() -> None:
    profile = ProfileIn(**valid())
    assert profile.timezone == "UTC"
    assert profile.cgpa_scale == 10
    assert profile.skills == []


def test_full_profile_is_valid_and_normalised() -> None:
    profile = ProfileIn(
        **valid(
            college="  IIT Madras ",
            degree="B.Tech CSE",
            current_year=3,
            cgpa="8.75",
            cgpa_scale=10,
            skills=["Python", "python", "C++", "React.js"],
            dream_company="Google",
            dream_role="SWE Intern",
            target_package_lpa="32.5",
            github_username="octocat",
            linkedin_url="https://www.linkedin.com/in/asha-k",
            leetcode_username="asha_k",
            codeforces_username="asha.k",
            timezone="Asia/Kolkata",
            daily_minutes=90,
            preferred_language="python",
        )
    )
    assert profile.college == "IIT Madras"
    assert profile.skills == ["Python", "C++", "React.js"]  # case-insensitive de-duplication


def test_blank_optional_fields_become_none() -> None:
    profile = ProfileIn(**valid(college="   ", github_username="", cgpa="", daily_minutes=""))
    assert profile.college is None
    assert profile.github_username is None
    assert profile.cgpa is None
    assert profile.daily_minutes is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "x" * 101),
        ("current_year", 0),
        ("current_year", 9),
        ("cgpa", "-1"),
        ("cgpa", "8.755"),
        ("cgpa_scale", 7),
        ("target_package_lpa", "-5"),
        ("github_username", "-bad-start"),
        ("github_username", "has space"),
        ("linkedin_url", "http://www.linkedin.com/in/asha"),
        ("linkedin_url", "https://evil.example/in/asha"),
        ("linkedin_url", "https://linkedin.com.evil.example/in/asha"),
        ("leetcode_username", "bad name!"),
        ("codeforces_username", "ab"),
        ("timezone", "Mars/Olympus"),
        ("daily_minutes", 5),
        ("daily_minutes", 721),
        ("preferred_language", "cobol"),
        ("skills", ["<script>"]),
        ("skills", ["x" * 41]),
    ],
)
def test_invalid_values_are_rejected(field: str, value: Any) -> None:
    with pytest.raises(ValidationError):
        ProfileIn(**valid(**{field: value}))


def test_cgpa_cannot_exceed_selected_scale() -> None:
    with pytest.raises(ValidationError, match="cannot exceed"):
        ProfileIn(**valid(cgpa="4.5", cgpa_scale=4))


def test_too_many_skills_rejected() -> None:
    with pytest.raises(ValidationError):
        ProfileIn(**valid(skills=[f"skill{i}" for i in range(31)]))


def test_unknown_fields_are_rejected_so_user_id_cannot_be_forged() -> None:
    with pytest.raises(ValidationError):
        ProfileIn(**valid(user_id="00000000-0000-0000-0000-000000000000"))
