"""Historical SQLite snapshots and independent SQL observations, not a migrator."""

from __future__ import annotations

import hashlib
import importlib
import secrets
import shutil
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from argon2 import PasswordHasher

from tests.mariadb_support import MariaDBServer, identifier
from tests.support import PASSWORD, Harness


def normalized(value: Any) -> Any:
    if isinstance(value, datetime):
        return (value.replace(tzinfo=UTC) if value.tzinfo is None else value).timestamp()
    if isinstance(value, Decimal):
        return float(value)
    return value


class MigrationSnapshot:
    def __init__(self, path: Path, harness: Harness, server: MariaDBServer) -> None:
        self.source = path / "historical.sqlite3"
        self.backup = path / "historical.backup.sqlite3"
        self.harness = harness
        self.server = server
        self.original_hash = PasswordHasher().hash(PASSWORD)
        self.token = secrets.token_urlsafe(32)
        self.expiry = harness.clock.origin.timestamp() + 300
        self.report: Any = None
        self.conflict = False
        self.before: dict[str, list[tuple[Any, ...]]] = {}
        self.source_hashes: tuple[str, str] | None = None
        self.target_before: dict[str, list[tuple[Any, ...]]] = {}
        # This is the existing SQLite schema, not the new MariaDB schema.
        with sqlite3.connect(self.source) as connection:
            connection.executescript("""
                CREATE TABLE members (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
                    failed_attempts INTEGER NOT NULL DEFAULT 0, locked_until REAL);
                CREATE TABLE sessions (token_hash TEXT PRIMARY KEY,
                    username TEXT NOT NULL REFERENCES members(username), expires_at REAL NOT NULL);
            """)

    def member(self, failures: int = 0, locked: bool = False) -> None:
        with sqlite3.connect(self.source) as connection:
            connection.execute("INSERT INTO members VALUES (?, ?, ?, ?)", (
                self.harness.username, self.original_hash, failures,
                self.harness.clock.origin.timestamp() + 60 if locked else None,
            ))

    def session(self, expired: bool = False) -> None:
        self.expiry = self.harness.clock.origin.timestamp() + (-1 if expired else 300)
        self.add_session(self.token, self.harness.username, self.expiry)
        # Restore the old browser's token from the source snapshot. No new login/token on target.
        self.harness.client.cookies.set("session_id", self.token)

    def add_session(self, token: str, username: str, expiry: float) -> None:
        with sqlite3.connect(self.source) as connection:
            connection.execute("INSERT INTO sessions VALUES (?, ?, ?)", (
                hashlib.sha256(token.encode()).hexdigest(), username, expiry,
            ))

    def source_rows(self) -> dict[str, list[tuple[Any, ...]]]:
        with sqlite3.connect(f"{self.source.as_uri()}?mode=ro", uri=True) as connection:
            tables = [row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )]
            return {table: list(connection.execute(f"SELECT * FROM {identifier(table)}"))
                    for table in tables}

    def freeze(self) -> None:
        # Every snapshot writer above is closed/committed before the real tool is called.
        self.before = self.source_rows()
        shutil.copy2(self.source, self.backup)
        self.source_hashes = self.hashes()

    def hashes(self) -> tuple[str, str]:
        return tuple_hash(self.source), tuple_hash(self.backup)

    def target_rows(self) -> dict[str, list[tuple[Any, ...]]]:
        """Compare raw target values using the tool's declared schema mapping, not its counts."""
        assert self.report is not None
        tables = self.report.table_mapping
        columns = self.report.column_mapping
        assert set(tables) == set(self.before), "Every SQLite application table needs a mapping"
        assert len(set(tables.values())) == len(tables), "Table mapping must not collapse tables"
        result = {}
        with sqlite3.connect(f"{self.source.as_uri()}?mode=ro", uri=True) as source:
            with self.server.connect(self.harness.settings.db_name) as connection:
                with connection.cursor() as cursor:
                    for table in self.before:
                        names = [row[1] for row in source.execute(
                            f"PRAGMA table_info({identifier(table)})")]
                        assert set(columns[table]) == set(names), "Source fields must not be omitted"
                        target_columns = [columns[table][name] for name in names]
                        assert len(set(target_columns)) == len(names)
                        selected = ", ".join(identifier(name) for name in target_columns)
                        cursor.execute(f"SELECT {selected} FROM {identifier(tables[table])}")
                        result[table] = [tuple(normalized(v) for v in row)
                                         for row in cursor.fetchall()]
        return result

    def raw_target(self) -> dict[str, list[tuple[Any, ...]]]:
        with self.server.connect(self.harness.settings.db_name) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall() if row[0] != "_bdd_test_owner"]
                result = {}
                for table in tables:
                    cursor.execute(f"SELECT * FROM {identifier(table)}")
                    result[table] = list(cursor.fetchall())
                return result

    def run(self, conflict: bool = False) -> None:
        if self.source_hashes is None:
            self.freeze()
        self.harness.close()  # No active application writes during migration.
        try:
            module = importlib.import_module("ai_bdd_demo.migration")
        except ModuleNotFoundError as exc:
            raise RuntimeError("Normal migration entry missing; see tests/README.md, not Red") from exc
        # Normal maintenance tool; no fake or reimplemented migration fallback.
        if conflict:
            try:
                module.migrate_sqlite_to_mariadb(
                    source_path=self.source, target_settings=self.harness.settings,
                )
            except module.MigrationConflictError:
                self.conflict = True
            else:
                raise AssertionError("Existing target member must produce an explicit conflict")
        else:
            self.report = module.migrate_sqlite_to_mariadb(
                source_path=self.source, target_settings=self.harness.settings,
            )
        assert self.hashes() == self.source_hashes, "Migration changed source or backup bytes"
        self.harness.restart()

    def assert_all_rows(self) -> None:
        actual = self.target_rows()
        assert set(actual) == set(self.before)
        for table, rows in self.before.items():
            assert len(actual[table]) == len(rows), f"Row count differs: {table}"
            assert sorted(actual[table], key=repr) == sorted(rows, key=repr), table


def tuple_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
