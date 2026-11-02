"""Explicit settings: production values are supplied by the operator."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class Settings(Protocol):
    @property
    def database_path(self) -> Path: ...
    @property
    def secret_key(self) -> str: ...
    @property
    def cookie_secure(self) -> bool: ...
    @property
    def session_ttl_seconds(self) -> int: ...
    @property
    def cookie_samesite(self) -> str: ...


@dataclass(frozen=True)
class AppSettings:
    database_path: Path
    secret_key: str
    cookie_secure: bool
    session_ttl_seconds: int
    cookie_samesite: str

    @classmethod
    def from_environment(cls) -> "AppSettings":
        """Fail closed when operator configuration is absent; no production defaults."""
        secure = os.environ["AI_BDD_COOKIE_SECURE"].lower()
        if secure not in {"true", "false"}:
            raise ValueError("AI_BDD_COOKIE_SECURE must be true or false")
        return cls(
            database_path=Path(os.environ["AI_BDD_DATABASE_PATH"]),
            secret_key=os.environ["AI_BDD_SECRET_KEY"],
            cookie_secure=secure == "true",
            session_ttl_seconds=int(os.environ["AI_BDD_SESSION_TTL_SECONDS"]),
            cookie_samesite=os.environ["AI_BDD_COOKIE_SAMESITE"],
        )


def validate(settings: Settings) -> None:
    if not Path(settings.database_path).is_absolute():
        raise ValueError("database_path must be absolute")
    if not settings.secret_key:
        raise ValueError("secret_key must be supplied externally")
    if settings.session_ttl_seconds <= 0:
        raise ValueError("session_ttl_seconds must be positive")
    if settings.cookie_samesite not in {"lax", "strict", "none"}:
        raise ValueError("Unsupported cookie_samesite")
    if settings.cookie_samesite == "none" and not settings.cookie_secure:
        raise ValueError("SameSite=None requires secure cookies")
