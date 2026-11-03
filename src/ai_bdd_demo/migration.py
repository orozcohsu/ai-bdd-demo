"""Explicit, read-only-source SQLite migration into a prepared, empty MariaDB schema."""

from __future__ import annotations

import hashlib
import math
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from ai_bdd_demo.config import Settings
from ai_bdd_demo.db import Connection, Database, DatabaseConflictError, DatabaseError, member_key


class MigrationError(RuntimeError):
    """Sanitized migration failure; source is never altered."""


class MigrationConflictError(MigrationError):
    """Existing target data or uniqueness conflict; no overwrites are performed."""


@dataclass(frozen=True)
class MigrationReport:
    table_mapping: dict[str, str]
    column_mapping: dict[str, dict[str, str]]
    row_counts: dict[str, int]


COLUMNS = {
    "members": ("username", "password_hash", "failed_attempts", "locked_until"),
    "sessions": ("token_hash", "username", "expires_at"),
}


def _snapshot(path: Path) -> tuple[list[sqlite3.Row], list[sqlite3.Row]]:
    if not path.is_file():
        raise MigrationError("Source SQLite snapshot does not exist")
    # A live WAL source is not a completed maintenance snapshot. Do not checkpoint/write it here.
    wal = Path(str(path) + "-wal")
    if wal.exists() and wal.stat().st_size:
        raise MigrationError("Source has an active WAL; prepare a consistent backup before migration")
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as source:
            source.row_factory = sqlite3.Row
            source.execute("PRAGMA query_only=ON")
            source.execute("BEGIN")
            if source.execute("PRAGMA quick_check").fetchall()[0][0] != "ok":
                raise MigrationError("Source integrity check failed")
            tables = {row[0] for row in source.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND substr(name,1,7) != 'sqlite_'"
            )}
            if tables != set(COLUMNS):
                raise MigrationError("Source application table inventory unsupported; nothing migrated")
            for table, expected in COLUMNS.items():
                # Identifiers are fixed application constants, not operator/user input.
                columns = {row[1] for row in source.execute(f'PRAGMA table_xinfo("{table}")')}
                if columns != set(expected):
                    raise MigrationError("Source column inventory unsupported; nothing migrated")
            members = source.execute(
                "SELECT username,password_hash,failed_attempts,locked_until FROM members"
            ).fetchall()
            sessions = source.execute("SELECT token_hash,username,expires_at FROM sessions").fetchall()
            return members, sessions
    except sqlite3.Error:
        raise MigrationError("Cannot read a consistent SQLite source snapshot") from None


def _valid_time(value: object, *, nullable: bool = False) -> bool:
    if value is None:
        return nullable
    return isinstance(value, (int, float)) and math.isfinite(value)


def _validate_rows(members: list[sqlite3.Row], sessions: list[sqlite3.Row]) -> None:
    names: set[str] = set()
    keys: set[bytes] = set()
    for row in members:
        username, password_hash, failures, deadline = tuple(row)
        if (not isinstance(username, str) or not isinstance(password_hash, str)
                or type(failures) is not int or not 0 <= failures <= 9223372036854775807
                or not _valid_time(deadline, nullable=True)):
            raise MigrationError("Source member data is incompatible; nothing migrated")
        key = member_key(username)
        if username in names or key in keys:
            raise MigrationConflictError("Source contains conflicting member identities")
        names.add(username)
        keys.add(key)
    tokens: set[str] = set()
    for row in sessions:
        token, username, expiry = tuple(row)
        if (not isinstance(token, str) or re.fullmatch(r"[0-9a-f]{64}", token) is None
                or not isinstance(username, str) or username not in names or not _valid_time(expiry)):
            raise MigrationError("Source Session data is incompatible; nothing migrated")
        if token in tokens:
            raise MigrationConflictError("Source contains duplicate Session identities")
        tokens.add(token)


def _copy(connection: Connection, members: list[sqlite3.Row], sessions: list[sqlite3.Row]) -> None:
    # Reject any populated application target, including otherwise non-overlapping members.
    # This tool is a full cutover, not a merge/upsert or schema migration.
    for statement in ("SELECT username_key FROM members LIMIT 1 FOR UPDATE",
                      "SELECT token_hash FROM sessions LIMIT 1 FOR UPDATE"):
        if connection.execute(statement).fetchone() is not None:
            raise MigrationConflictError("Target application data already exists; nothing overwritten")
    for row in members:
        connection.execute(
            "INSERT INTO members(username_key,username,password_hash,failed_attempts,locked_until) "
            "VALUES (%s,%s,%s,%s,%s)", (member_key(row["username"]), *tuple(row)),
        )
    for row in sessions:
        connection.execute(
            "INSERT INTO sessions(token_hash,username,expires_at,username_key) VALUES (%s,%s,%s,%s)",
            (*tuple(row), member_key(row["username"])),
        )
    # Verify actual values before commit, not only affected row counts.
    actual_members = connection.execute(
        "SELECT username,password_hash,failed_attempts,locked_until FROM members"
    ).fetchall()
    actual_sessions = connection.execute("SELECT token_hash,username,expires_at FROM sessions").fetchall()
    for expected, actual, columns in ((members, actual_members, COLUMNS["members"]),
                                      (sessions, actual_sessions, COLUMNS["sessions"])):
        before = sorted((tuple(row) for row in expected), key=repr)
        after = sorted((tuple(row[column] for column in columns) for row in actual), key=repr)
        if before != after:
            raise MigrationError("Target value verification failed; migration rolled back")


def migrate_sqlite_to_mariadb(*, source_path: Path, target_settings: Settings) -> MigrationReport:
    """Caller must stop writes and back up first. No DDL, service switching or source writes."""
    source_path = source_path.resolve(strict=True)
    source_hash = hashlib.sha256(source_path.read_bytes()).digest()
    members, sessions = _snapshot(source_path)
    _validate_rows(members, sessions)
    database = Database(target_settings)
    database.check_schema()
    try:
        with database.connection(write=True) as connection:
            _copy(connection, members, sessions)
            if hashlib.sha256(source_path.read_bytes()).digest() != source_hash:
                raise MigrationError("Source changed during migration; target rolled back")
    except DatabaseConflictError:
        raise MigrationConflictError("Target data conflict; migration rolled back") from None
    except DatabaseError:
        # A lost connection during commit can make the outcome unknowable to the client.
        raise MigrationError("MariaDB migration failed; verify target before retry or cutover") from None
    return MigrationReport(
        table_mapping={table: table for table in COLUMNS},
        column_mapping={table: {column: column for column in columns}
                        for table, columns in COLUMNS.items()},
        row_counts={"members": len(members), "sessions": len(sessions)},
    )
