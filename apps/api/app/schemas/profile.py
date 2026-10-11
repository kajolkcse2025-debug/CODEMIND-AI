"""Profile request/response models. Validation here is the source of truth for the API."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal, Self
from zoneinfo import available_timezones

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

PreferredLanguage = Literal["python", "java", "cpp"]
CgpaScale = Literal[4, 5, 10]

_GITHUB = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_LEETCODE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
_CODEFORCES = re.compile(r"^[A-Za-z0-9_.-]{3,24}$")
_LINKEDIN = re.compile(r"^https://([a-z]{2,3}\.)?linkedin\.com/in/[\w\-%]{3,100}/?$", re.IGNORECASE)
_SKILL = re.compile(r"^\w[\w +#.\-/()]*$")
_TIMEZONES = available_timezones()

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=120)]


def _blank_to_none(value: object) -> object:
    if isinstance(value, str) and not value.strip():
        return None
    return value


class ProfileIn(BaseModel):
    """Used for both POST (create) and PUT (full replacement of the editable fields).

    Unknown fields are rejected, so a client can never smuggle in ``user_id`` or similar.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    college: ShortText | None = None
    degree: ShortText | None = None
    current_year: Annotated[int, Field(ge=1, le=8)] | None = None
    cgpa: Annotated[Decimal, Field(ge=0, max_digits=4, decimal_places=2)] | None = None
    cgpa_scale: CgpaScale = 10
    skills: Annotated[list[str], Field(max_length=30)] = Field(default_factory=list)
    dream_company: ShortText | None = None
    dream_role: ShortText | None = None
    target_package_lpa: Annotated[Decimal, Field(ge=0, lt=10000, decimal_places=2)] | None = None
    github_username: str | None = None
    linkedin_url: Annotated[str, Field(max_length=200)] | None = None
    leetcode_username: str | None = None
    codeforces_username: str | None = None
    timezone: str = "UTC"
    daily_minutes: Annotated[int, Field(ge=15, le=720)] | None = None
    preferred_language: PreferredLanguage | None = None

    @field_validator(
        "college",
        "degree",
        "current_year",
        "cgpa",
        "dream_company",
        "dream_role",
        "target_package_lpa",
        "github_username",
        "linkedin_url",
        "leetcode_username",
        "codeforces_username",
        "daily_minutes",
        "preferred_language",
        mode="before",
    )
    @classmethod
    def _empty_means_unset(cls, value: object) -> object:
        return _blank_to_none(value)

    @field_validator("github_username")
    @classmethod
    def _github(cls, value: str | None) -> str | None:
        if value is not None and not _GITHUB.match(value):
            raise ValueError("must be a valid GitHub username")
        return value

    @field_validator("leetcode_username")
    @classmethod
    def _leetcode(cls, value: str | None) -> str | None:
        if value is not None and not _LEETCODE.match(value):
            raise ValueError("may contain letters, digits, '_' and '-' (max 40)")
        return value

    @field_validator("codeforces_username")
    @classmethod
    def _codeforces(cls, value: str | None) -> str | None:
        if value is not None and not _CODEFORCES.match(value):
            raise ValueError("must be 3-24 characters: letters, digits, '_', '-' or '.'")
        return value

    @field_validator("linkedin_url")
    @classmethod
    def _linkedin(cls, value: str | None) -> str | None:
        if value is not None and not _LINKEDIN.match(value):
            raise ValueError("must be an https://linkedin.com/in/<name> profile URL")
        return value

    @field_validator("timezone")
    @classmethod
    def _timezone(cls, value: str) -> str:
        if value not in _TIMEZONES:
            raise ValueError("must be a valid IANA time zone, for example 'Asia/Kolkata'")
        return value

    @field_validator("skills")
    @classmethod
    def _skills(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw in value:
            skill = raw.strip()
            if not 1 <= len(skill) <= 40 or not _SKILL.match(skill):
                raise ValueError(
                    f"invalid skill {raw!r}: use 1-40 letters, digits or + # . - / ( )"
                )
            key = skill.casefold()
            if key not in seen:
                seen.add(key)
                cleaned.append(skill)
        return cleaned

    @model_validator(mode="after")
    def _cgpa_within_scale(self) -> Self:
        if self.cgpa is not None and self.cgpa > self.cgpa_scale:
            raise ValueError(f"cgpa cannot exceed the selected scale of {self.cgpa_scale}")
        return self


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    college: str | None
    degree: str | None
    current_year: int | None
    cgpa: float | None
    cgpa_scale: int
    skills: list[str]
    dream_company: str | None
    dream_role: str | None
    target_package_lpa: float | None
    github_username: str | None
    linkedin_url: str | None
    leetcode_username: str | None
    codeforces_username: str | None
    timezone: str
    daily_minutes: int | None
    preferred_language: str | None
    created_at: datetime
    updated_at: datetime
