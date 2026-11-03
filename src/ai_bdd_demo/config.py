"""Explicit MariaDB settings; secrets are excluded from repr."""

import os
from dataclasses import dataclass, field
from typing import Protocol


class Settings(Protocol):
    @property
    def db_host(self) -> str: ...
    @property
    def db_port(self) -> int: ...
    @property
    def db_name(self) -> str: ...
    @property
    def db_user(self) -> str: ...
    @property
    def db_password(self) -> str: ...
    @property
    def db_connect_timeout_seconds(self) -> int: ...
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
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str = field(repr=False)
    secret_key: str = field(repr=False)
    cookie_secure: bool
    session_ttl_seconds: int
    cookie_samesite: str
    db_connect_timeout_seconds: int = 10

    @classmethod
    def from_environment(cls) -> "AppSettings":
        def required(name: str) -> str:
            value = os.environ.get(name)
            if not value:
                raise ValueError(f"Missing required configuration: {name}")
            return value

        def number(name: str, default: str | None = None) -> int:
            value = required(name) if default is None else os.environ.get(name, default)
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Invalid integer configuration: {name}") from None

        secure = required("AI_BDD_COOKIE_SECURE").lower()
        if secure not in {"true", "false"}:
            raise ValueError("AI_BDD_COOKIE_SECURE must be true or false")
        result = cls(
            db_host=required("AI_BDD_DB_HOST"), db_port=number("AI_BDD_DB_PORT"),
            db_name=required("AI_BDD_DB_NAME"), db_user=required("AI_BDD_DB_USER"),
            db_password=required("AI_BDD_DB_PASSWORD"), secret_key=required("AI_BDD_SECRET_KEY"),
            cookie_secure=secure == "true", session_ttl_seconds=number("AI_BDD_SESSION_TTL_SECONDS"),
            cookie_samesite=required("AI_BDD_COOKIE_SAMESITE"),
            db_connect_timeout_seconds=number("AI_BDD_DB_CONNECT_TIMEOUT_SECONDS", "10"),
        )
        validate(result)
        return result


def validate(settings: Settings) -> None:
    for name in ("db_host", "db_name", "db_user", "db_password", "secret_key"):
        if not isinstance(getattr(settings, name), str) or not getattr(settings, name):
            raise ValueError(f"{name} must be supplied externally")
    if type(settings.db_port) is not int or not 1 <= settings.db_port <= 65535:
        raise ValueError("db_port must be a valid TCP port")
    if type(settings.db_connect_timeout_seconds) is not int or settings.db_connect_timeout_seconds <= 0:
        raise ValueError("db_connect_timeout_seconds must be positive")
    if type(settings.session_ttl_seconds) is not int or settings.session_ttl_seconds <= 0:
        raise ValueError("session_ttl_seconds must be positive")
    if type(settings.cookie_secure) is not bool:
        raise ValueError("cookie_secure must be a boolean")
    if settings.cookie_samesite not in {"lax", "strict", "none"}:
        raise ValueError("Unsupported cookie_samesite")
    if settings.cookie_samesite == "none" and not settings.cookie_secure:
        raise ValueError("SameSite=None requires secure cookies")
