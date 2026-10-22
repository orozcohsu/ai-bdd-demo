"""Authentication, persistent lockout and server-side session services."""

import hashlib
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from ai_bdd_demo.db import Database, Members

ERROR = "帳號或密碼錯誤"
LOCKED = "登入暫時受限，請於 1 分鐘後再試"


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True)
class AccountState:
    failed_attempts: int
    locked_until: datetime | None
    is_locked: bool


@dataclass(frozen=True)
class Session:
    username: str
    expires_at: datetime


class Sessions:
    def __init__(self, database: Database, clock: Clock, ttl: int) -> None:
        self.database, self.clock, self.ttl = database, clock, ttl

    def issue(self, connection: sqlite3.Connection, username: str) -> str:
        token = secrets.token_urlsafe(32)
        expiry = self.clock.now() + timedelta(seconds=self.ttl)
        connection.execute("INSERT INTO sessions VALUES (?, ?, ?)",
                           (self.digest(token), username, expiry.timestamp()))
        return token

    @staticmethod
    def digest(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def get(self, session_id: str) -> Session | None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT username, expires_at FROM sessions WHERE token_hash=?",
                                     (self.digest(session_id),)).fetchone()
        if row is None or row["expires_at"] <= self.clock.now().timestamp():
            return None
        return Session(row["username"], datetime.fromtimestamp(row["expires_at"], UTC))


@dataclass(frozen=True)
class LoginResult:
    session_id: str | None = None
    message: str = ERROR


class Authentication:
    def __init__(self, database: Database, members: Members, sessions: Sessions,
                 clock: Clock) -> None:
        self.database, self.members, self.sessions, self.clock = database, members, sessions, clock
        self.hasher = PasswordHasher()
        # Equal-cost verification for absent members; never a default account/password.
        self.absent_hash = self.hasher.hash(secrets.token_urlsafe(32))

    def _state(self, connection: sqlite3.Connection, username: str) -> AccountState | None:
        row = connection.execute("SELECT failed_attempts, locked_until FROM members WHERE username=?",
                                 (username,)).fetchone()
        if row is None:
            return None
        deadline = row["locked_until"]
        if deadline is not None and deadline <= self.clock.now().timestamp():
            connection.execute("UPDATE members SET failed_attempts=0, locked_until=NULL "
                               "WHERE username=?", (username,))
            return AccountState(0, None, False)
        until = None if deadline is None else datetime.fromtimestamp(deadline, UTC)
        return AccountState(row["failed_attempts"], until, until is not None)

    def get_account_state(self, username: str) -> AccountState | None:
        with self.database.connection(write=True) as connection:
            return self._state(connection, username)

    def authenticate(self, username: str, password: str) -> LoginResult:
        member = self.members.get(username)
        valid: bool
        try:
            valid = self.hasher.verify(self.absent_hash if member is None else member.password_hash,
                                       password)
        except (VerificationError, InvalidHashError):
            valid = False
        if member is None:
            return LoginResult()
        with self.database.connection(write=True) as connection:
            state = self._state(connection, username)
            if state is None:
                return LoginResult()
            if state.is_locked:
                return LoginResult(message=LOCKED)
            if valid:
                connection.execute("UPDATE members SET failed_attempts=0, locked_until=NULL "
                                   "WHERE username=?", (username,))
                return LoginResult(session_id=self.sessions.issue(connection, username))
            failures = state.failed_attempts + 1
            deadline = (self.clock.now() + timedelta(seconds=60)).timestamp() if failures >= 3 else None
            connection.execute("UPDATE members SET failed_attempts=?, locked_until=? WHERE username=?",
                               (failures, deadline, username))
            return LoginResult(message=LOCKED if deadline is not None else ERROR)


@dataclass(frozen=True)
class Services:
    members: Members
    auth: Authentication
    sessions: Sessions
