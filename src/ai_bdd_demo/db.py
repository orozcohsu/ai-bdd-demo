"""Operation-scoped MariaDB connections, transactions and explicit schema preparation."""

from __future__ import annotations

import hashlib
import importlib
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, cast

from ai_bdd_demo.config import Settings, validate


class DatabaseError(RuntimeError):
    """Sanitized failure, containing neither parameters nor driver diagnostics."""


class DatabaseConflictError(DatabaseError):
    """Uniqueness conflict; the enclosing transaction must roll back."""


def member_key(username: str) -> bytes:
    return hashlib.sha256(username.encode("utf-8")).digest()


class Result:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def fetchone(self) -> dict[str, Any] | None:
        return self.rows[0] if self.rows else None

    def fetchall(self) -> list[dict[str, Any]]:
        return self.rows


class Connection:
    def __init__(self, raw: Any, driver: Any) -> None:
        self.raw, self.driver = raw, driver

    def execute(self, sql: str, parameters: tuple[object, ...] = ()) -> Result:
        try:
            with self.raw.cursor() as cursor:
                cursor.execute(sql, parameters)
                return Result(list(cursor.fetchall()) if cursor.description is not None else [])
        except self.driver.MySQLError as exc:
            if exc.args and exc.args[0] == 1062:
                raise DatabaseConflictError("Database uniqueness conflict") from None
            raise DatabaseError("MariaDB operation failed; inspect protected server diagnostics") from None


class Database:
    def __init__(self, settings: Settings) -> None:
        validate(settings)
        self._settings = settings

    @contextmanager
    def connection(self, *, write: bool = False) -> Iterator[Connection]:
        try:
            driver = importlib.import_module("pymysql")
        except ModuleNotFoundError:
            raise DatabaseError("MariaDB driver missing: install PyMySQL") from None
        s = self._settings
        try:
            raw = driver.connect(
                host=s.db_host, port=s.db_port, database=s.db_name,
                user=s.db_user, password=s.db_password, charset="utf8mb4",
                cursorclass=driver.cursors.DictCursor, autocommit=False,
                connect_timeout=s.db_connect_timeout_seconds,
                read_timeout=s.db_connect_timeout_seconds,
                write_timeout=s.db_connect_timeout_seconds, local_infile=False,
                init_command="SET time_zone='+00:00', "
                             "sql_mode='STRICT_ALL_TABLES,NO_ENGINE_SUBSTITUTION'",
            )
        except driver.MySQLError:
            raise DatabaseError("Cannot connect to configured MariaDB database") from None
        try:
            yield Connection(raw, driver)
            try:
                if write:
                    raw.commit()
                else:
                    raw.rollback()
            except driver.MySQLError:
                raise DatabaseError("Transaction completion failed; verify outcome before retry") from None
        except BaseException:
            try:
                raw.rollback()
            except driver.MySQLError:
                raise DatabaseError("Rollback failed; transaction outcome requires verification") from None
            raise
        finally:
            raw.close()

    def check_schema(self) -> None:
        with self.connection() as connection:
            for table in TABLES:
                validate_table(connection, self._settings.db_name, table, required=True)


TABLES = {
    "members": """CREATE TABLE members (
        username_key BINARY(32) PRIMARY KEY,
        username LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        password_hash LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        failed_attempts BIGINT NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
        locked_until DOUBLE NULL
    ) ENGINE=InnoDB""",
    "sessions": """CREATE TABLE sessions (
        token_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
        username LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
        username_key BINARY(32) NOT NULL,
        expires_at DOUBLE NOT NULL,
        FOREIGN KEY (username_key) REFERENCES members(username_key)
    ) ENGINE=InnoDB""",
}
TEXT_STORAGE = "longtext"
FINGERPRINT_STORAGE = "char"
EXPECTED = {
    "members": {"username_key": "binary", "username": TEXT_STORAGE, "password_hash": TEXT_STORAGE,
                "failed_attempts": "bigint", "locked_until": "double"},
    "sessions": {"token_hash": FINGERPRINT_STORAGE, "username": TEXT_STORAGE, "username_key": "binary",
                 "expires_at": "double"},
}


def validate_table(connection: Connection, schema: str, table: str, *, required: bool) -> bool:
    record = connection.execute(
        "SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s",
        (schema, table),
    ).fetchone()
    if record is None:
        if required:
            raise DatabaseError("Required tables absent; run initialize_schema explicitly")
        return False
    if record["ENGINE"] != "InnoDB":
        raise DatabaseError("Existing application table must use InnoDB")
    columns = connection.execute(
        "SELECT COLUMN_NAME, DATA_TYPE, COLUMN_KEY, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH, "
        "COLLATION_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s",
        (schema, table),
    ).fetchall()
    if {r["COLUMN_NAME"]: r["DATA_TYPE"] for r in columns} != EXPECTED[table]:
        raise DatabaseError("Incompatible application columns; explicit migration required")
    for column in columns:
        name = column["COLUMN_NAME"]
        if column["IS_NULLABLE"] != ("YES" if name == "locked_until" else "NO"):
            raise DatabaseError("Incompatible column nullability")
        if name == "username_key" and column["CHARACTER_MAXIMUM_LENGTH"] != 32:
            raise DatabaseError("Incompatible member key width")
        if name == "token_hash" and (column["CHARACTER_MAXIMUM_LENGTH"] != 64
                                     or column["COLLATION_NAME"] != "ascii_bin"):
            raise DatabaseError("Incompatible Session fingerprint representation")
        if column["DATA_TYPE"] == "longtext" and column["COLLATION_NAME"] != "utf8mb4_bin":
            raise DatabaseError("Incompatible application text encoding")
    primary = "username_key" if table == "members" else "token_hash"
    if [c["COLUMN_NAME"] for c in columns if c["COLUMN_KEY"] == "PRI"] != [primary]:
        raise DatabaseError("Incompatible primary key")
    if table == "sessions":
        foreign = connection.execute(
            "SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
            "FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s "
            "AND REFERENCED_TABLE_NAME IS NOT NULL", (schema, table),
        ).fetchall()
        if not any(r["COLUMN_NAME"] == "username_key" and r["REFERENCED_TABLE_NAME"] == "members"
                   and r["REFERENCED_COLUMN_NAME"] == "username_key" for r in foreign):
            raise DatabaseError("Required Session/member foreign key absent")
    return True


def initialize_schema(*, settings: Settings) -> None:
    """Explicit preparation, not startup or a data migration. Database must exist."""
    database = Database(settings)
    with database.connection(write=True) as connection:
        # Validate all existing tables before DDL, which MariaDB implicitly commits.
        present = {table: validate_table(connection, settings.db_name, table, required=False)
                   for table in TABLES}
        for table, statement in TABLES.items():
            if not present[table]:
                connection.execute(statement)
    database.check_schema()


@dataclass(frozen=True)
class Member:
    username: str
    password_hash: str


class Members:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, username: str, password_hash: str) -> None:
        with self.database.connection(write=True) as connection:
            connection.execute("INSERT INTO members(username_key,username,password_hash) VALUES (%s,%s,%s)",
                               (member_key(username), username, password_hash))

    def get(self, username: str) -> Member | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT username,password_hash FROM members WHERE username_key=%s",
                (member_key(username),),
            ).fetchone()
        if row is None or row["username"] != username:
            return None
        return Member(cast(str, row["username"]), cast(str, row["password_hash"]))
