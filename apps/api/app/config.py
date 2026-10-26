"""Application settings, read from environment variables only.

No secret has a default value. Anything sensitive is a ``SecretStr`` so it cannot be
printed by accident. Missing required values make the process fail fast at startup.
"""

import os
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = "development"
    log_level: str = "INFO"

    # Infrastructure (required: no defaults, so nothing is silently hard-coded).
    database_url: str
    redis_url: str

    # Browser origins allowed by CORS. Never "*".
    cors_allowed_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    # Firebase Authentication (token verification only; the frontend owns sign-in).
    firebase_project_id: str | None = None
    firebase_service_account_b64: SecretStr | None = None

    # AI. Phase 1 never calls a provider; these only configure the abstraction.
    ai_provider: Literal["gemini", "fake"] = "gemini"
    gemini_api_key: SecretStr | None = None
    ai_model_fast: str | None = None
    ai_model_strong: str | None = None
    # Code execution through an external sandbox (Judge0).
    judge0_base_url: str | None = None
    judge0_api_key: SecretStr | None = None
    judge0_timeout_sec: int = 15

    @field_validator(
        "firebase_project_id",
        "firebase_service_account_b64",
        "gemini_api_key",
        "ai_model_fast",
        "ai_model_strong",
        mode="before",
    )
    @classmethod
    def _blank_means_unset(cls, value: object) -> object:
        """``KEY=`` in an .env file means "not set", not "set to an empty string"."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("database_url")
    @classmethod
    def _normalise_database_url(cls, value: str) -> str:
        """Railway and others hand out ``postgres://`` or ``postgresql://`` URLs."""
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value[len(prefix) :]
        return value

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("["):
                import json

                return json.loads(stripped)
            return [part.strip() for part in stripped.split(",") if part.strip()]
        return value

    @field_validator("cors_allowed_origins")
    @classmethod
    def _no_wildcard_origin(cls, value: list[str]) -> list[str]:
        if "*" in value:
            raise ValueError("CORS_ALLOWED_ORIGINS must list explicit origins, never '*'")
        return value

    @property
    def firebase_emulator_enabled(self) -> bool:
        return bool(os.environ.get("FIREBASE_AUTH_EMULATOR_HOST"))

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @model_validator(mode="after")
    def _production_requirements(self) -> "Settings":
        if self.environment in ("staging", "production"):
            if self.firebase_emulator_enabled:
                raise ValueError(
                    "The Firebase emulator must not be enabled in staging or production"
                )
            if not self.firebase_project_id or self.firebase_service_account_b64 is None:
                raise ValueError(
                    "FIREBASE_PROJECT_ID and FIREBASE_SERVICE_ACCOUNT_B64 are required "
                    f"when ENVIRONMENT={self.environment}"
                )
            if self.ai_provider == "fake":
                raise ValueError(
                    f"AI_PROVIDER=fake is not allowed when ENVIRONMENT={self.environment}"
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
