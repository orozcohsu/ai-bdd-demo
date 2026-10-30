"""Short-lived SQLite connections and atomic writes, independent of HTTP."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    @contextmanager
    def connection(self, *, write: bool = False) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            if write:
                connection.execute("BEGIN IMMEDIATE")
            yield connection
            if write:
                connection.commit()
        except Exception:
            if write:
                connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection(write=True) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS members (
                    username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
                    failed_attempts INTEGER NOT NULL DEFAULT 0,
                    locked_until REAL
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    username TEXT NOT NULL REFERENCES members(username),
                    expires_at REAL NOT NULL
                )
            """)


@dataclass(frozen=True)
class Member:
    username: str
    password_hash: str


class Members:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, username: str, password_hash: str) -> None:
        with self.database.connection(write=True) as connection:
            connection.execute("INSERT INTO members(username, password_hash) VALUES (?, ?)",
                               (username, password_hash))

    def get(self, username: str) -> Member | None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT username, password_hash FROM members WHERE username=?",
                                     (username,)).fetchone()
        return None if row is None else Member(row["username"], row["password_hash"])
