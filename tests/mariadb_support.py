"""Disposable local/Runner MariaDB provisioning; never reads application DB settings."""

from __future__ import annotations

import importlib
import ipaddress
import os
import re
import secrets
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


def identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", value):
        raise ValueError("Unsafe SQL identifier in test inspection")
    return f"`{value}`"


@dataclass(frozen=True)
class TestSettings:
    __test__ = False
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str = field(repr=False)
    secret_key: str = field(repr=False)
    db_connect_timeout_seconds: int = 10
    cookie_secure: bool = False
    session_ttl_seconds: int = 300
    cookie_samesite: str = "lax"


class MariaDBServer:
    def __init__(self) -> None:
        names = ("HOST", "PORT", "USER", "PASSWORD", "SERVER_ID", "DISPOSABLE")
        values = {name: os.environ.get(f"AI_BDD_TEST_DB_{name}") for name in names}
        if any(not value for value in values.values()):
            raise RuntimeError("Missing AI_BDD_TEST_DB_* settings; no production/SQLite fallback")
        if values["DISPOSABLE"] != "YES":
            raise RuntimeError("Explicit disposable test service acknowledgement required")
        self.host = str(values["HOST"])
        try:
            local = ipaddress.ip_address(self.host).is_loopback
        except ValueError:
            local = self.host in {"localhost", "mariadb"}
        if not local:
            raise RuntimeError("Only loopback or Runner service alias mariadb is allowed")
        self.port = int(str(values["PORT"]))
        self.user = str(values["USER"])
        self._password = str(values["PASSWORD"])
        self.expected_id = int(str(values["SERVER_ID"]))
        self.owned: dict[str, str] = {}
        try:
            self.driver = importlib.import_module("pymysql")
        except ModuleNotFoundError as exc:
            raise RuntimeError("DevOps must install PyMySQL test inspection driver") from exc

    def connect(self, database: str | None = None) -> Any:
        # Never propagate driver diagnostics containing credentials to pytest output.
        try:
            connection = self.driver.connect(
                host=self.host, port=self.port, user=self.user, password=self._password,
                database=database, connect_timeout=3, read_timeout=10, write_timeout=10,
                autocommit=True, charset="utf8mb4",
            )
        except self.driver.MySQLError:
            raise RuntimeError("Isolated MariaDB unavailable; check test-only service/settings") from None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION(), @@server_id")
                version, server_id = cursor.fetchone()
                if not str(version).startswith("11.8.6-MariaDB"):
                    raise RuntimeError("Test service must be MariaDB 11.8.6")
                if int(server_id) != self.expected_id:
                    raise RuntimeError("Test service identity mismatch; refusing access")
                cursor.execute("SET time_zone = '+00:00'")
        except BaseException:
            connection.close()
            raise
        return connection

    def wait_ready(self) -> None:
        deadline = time.monotonic() + 20
        while True:
            try:
                self.connect().close()
                return
            except RuntimeError as exc:
                if "unavailable" not in str(exc) or time.monotonic() >= deadline:
                    raise
                time.sleep(0.2)  # Service readiness only; never business clock waiting.

    @contextmanager
    def database(self) -> Iterator[TestSettings]:
        name = f"bdd_test_{secrets.token_hex(16)}"
        token = secrets.token_hex(32)
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE {identifier(name)}")
        self.owned[name] = token
        # A failed ownership-marker setup intentionally leaves the DB for inspection.
        with self.connect(name) as connection, connection.cursor() as cursor:
            cursor.execute("CREATE TABLE _bdd_test_owner (token VARCHAR(64) NOT NULL)")
            cursor.execute("INSERT INTO _bdd_test_owner VALUES (%s)", (token,))
        settings = TestSettings(self.host, self.port, name, self.user, self._password,
                                secrets.token_urlsafe(32))
        try:
            yield settings
        finally:
            self.drop_owned(name, token)

    def drop_owned(self, name: str, token: str) -> None:
        if not re.fullmatch(r"bdd_test_[0-9a-f]{32}", name) or self.owned.get(name) != token:
            raise RuntimeError("Refusing cleanup: database is not owned by this test process")
        # connect rechecks actual version and server identity before every operation.
        with self.connect(name) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT token FROM _bdd_test_owner")
            if cursor.fetchall() != ((token,),):
                raise RuntimeError("Refusing cleanup: ownership marker mismatch")
        with self.connect() as connection, connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE {identifier(name)}")
        del self.owned[name]
