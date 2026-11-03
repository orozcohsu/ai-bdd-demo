"""MariaDB restart and migration steps, executed only against the real application/tool."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pytest_bdd import given, then, when

from tests.mariadb_support import MariaDBServer
from tests.migration_support import MigrationSnapshot
from tests.support import PASSWORD, Harness


@pytest.fixture
def migration(tmp_path: Path, harness: Harness,
              mariadb_server: MariaDBServer) -> MigrationSnapshot:
    return MigrationSnapshot(tmp_path, harness, mariadb_server)


@given("已記錄該登入狀態原本的到期時間")
def remember_expiry(harness: Harness) -> None:
    matches = harness.authenticated_sessions()
    assert len(matches) == 1
    harness.saved_expiry = matches[0][1].expires_at


@when("在原到期時間之前使用原瀏覽器的 Session 存取 Welcome 頁面")
def access_before_expiry(harness: Harness) -> None:
    assert harness.saved_expiry is not None
    harness.clock.at(1)
    assert harness.clock.now() < harness.saved_expiry
    harness.response = harness.client.get("/welcome")


@then("該登入狀態仍使用原本的到期時間")
def unchanged_expiry(harness: Harness) -> None:
    sessions = harness.authenticated_sessions()
    assert len(sessions) == 1
    assert sessions[0][1].expires_at == harness.saved_expiry


@given("隔離 SQLite 來源含有會員、密碼雜湊、失敗次數、鎖定期限及 Session 資料")
def full_source(migration: MigrationSnapshot) -> None:
    migration.member(3, locked=True)
    with sqlite3.connect(migration.source) as connection:
        connection.execute("INSERT INTO members VALUES (?, ?, ?, ?)", (
            "另一會員", migration.original_hash, 1, None,
        ))


@given("Session 資料同時包含尚未到期及已過期的記錄")
def mixed_sessions(migration: MigrationSnapshot) -> None:
    migration.session()
    migration.add_session("isolated-expired-token", "另一會員",
                          migration.harness.clock.origin.timestamp() - 1)


@given("已備份來源並記錄全部應用資料表的資料筆數與欄位值")
def backup_source(migration: MigrationSnapshot) -> None:
    migration.freeze()


@given("隔離 MariaDB 目標已準備必要結構且沒有待遷移資料")
def empty_target(migration: MigrationSnapshot) -> None:
    assert migration.raw_target(), "initialize_schema must prepare application tables"
    assert all(not rows for rows in migration.raw_target().values())


@when("停止來源寫入並執行 SQLite 至 MariaDB 的全量遷移")
@when("將來源資料完整遷移並切換應用至隔離 MariaDB")
def migrate(migration: MigrationSnapshot) -> None:
    migration.run()


@then("全部應用資料表對應的資料均已搬移至 MariaDB")
@then("目標資料筆數與對應欄位值均與來源記錄一致")
def all_rows(migration: MigrationSnapshot) -> None:
    migration.assert_all_rows()


@then("會員與 Session 的資料關聯維持一致")
def relationships(migration: MigrationSnapshot) -> None:
    rows = migration.target_rows()
    members = {row[0] for row in rows["members"]}
    assert rows["sessions"]
    assert all(row[1] in members for row in rows["sessions"])


@then("已過期的 Session 記錄也保留原有資料")
def expired_rows(migration: MigrationSnapshot) -> None:
    rows = migration.target_rows()["sessions"]
    expired = [row for row in migration.before["sessions"]
               if row[2] <= migration.harness.clock.now().timestamp()]
    assert expired
    assert all(row in rows for row in expired)


@then("來源 SQLite 資料與備份未被刪除或改寫")
def protected_source(migration: MigrationSnapshot) -> None:
    assert migration.hashes() == migration.source_hashes
    assert migration.source_rows() == migration.before


@given("隔離 SQLite 中有一個未鎖定的會員及其有效密碼雜湊")
def unlocked_source(migration: MigrationSnapshot) -> None:
    migration.member()


@given("已記錄該會員原本的密碼雜湊")
def recorded_hash(migration: MigrationSnapshot) -> None:
    assert migration.source_rows()["members"][0][1] == migration.original_hash


@then("該會員儲存的密碼雜湊與遷移前完全相同")
def unchanged_hash(migration: MigrationSnapshot) -> None:
    record = migration.harness.services.members.get(migration.harness.username)
    assert record.password_hash == migration.original_hash
    migration.assert_all_rows()


@when("使用者以原帳號與原正確密碼登入")
def original_login(harness: Harness) -> None:
    harness.login(PASSWORD)


@given("隔離 SQLite 中有一個未鎖定且連續登入失敗次數為 2 的會員帳號")
def two_failures(migration: MigrationSnapshot) -> None:
    migration.member(2)


@then("該會員的連續登入失敗次數仍為 2")
def retained_count(migration: MigrationSnapshot) -> None:
    assert migration.harness.state().failed_attempts == 2
    migration.assert_all_rows()


@given("隔離 SQLite 中一個會員在時間 T 因第三次連續登入失敗被鎖定")
def locked_source(migration: MigrationSnapshot) -> None:
    migration.member(3, locked=True)


@when("在時間 T 後 30 秒完成遷移並切換應用至隔離 MariaDB")
def migrate_at_thirty(migration: MigrationSnapshot) -> None:
    migration.harness.clock.at(30)
    migration.run()
    migration.assert_all_rows()
    assert migration.harness.state().locked_until == datetime.fromtimestamp(
        migration.harness.clock.origin.timestamp() + 60, UTC)


@given("隔離 SQLite 中已有一個成功登入會員的有效 Session")
def valid_source_session(migration: MigrationSnapshot) -> None:
    migration.member()
    migration.session()


@given("已記錄該 Session 原本的到期時間 E")
def record_e(migration: MigrationSnapshot) -> None:
    assert migration.expiry > migration.harness.clock.now().timestamp()


@given("遷移期間保留原有 Cookie 行為與必要應用機密設定")
def preserve_settings(migration: MigrationSnapshot) -> None:
    assert migration.harness.client.cookies.get("session_id") == migration.token
    assert migration.harness.settings.secret_key


@when("在時間 E 之前完成遷移並切換應用至隔離 MariaDB")
def migrate_before_e(migration: MigrationSnapshot) -> None:
    migration.harness.clock.at(30)
    assert migration.harness.clock.now().timestamp() < migration.expiry
    migration.run()
    migration.assert_all_rows()


@when("在時間 E 之前使用原瀏覽器的 Session 存取 Welcome 頁面且未重新登入")
def original_cookie(migration: MigrationSnapshot) -> None:
    harness = migration.harness
    assert harness.client.cookies.get("session_id") == migration.token
    harness.response = harness.client.get("/welcome")


@then("該登入狀態的到期時間仍為 E")
def original_e(migration: MigrationSnapshot) -> None:
    record = migration.harness.services.sessions.get(migration.token)
    assert record is not None
    assert record.expires_at == datetime.fromtimestamp(migration.expiry, UTC)


@when("時間到達 E 並使用同一 Session 存取 Welcome 頁面")
def expires_at_e(migration: MigrationSnapshot) -> None:
    harness = migration.harness
    harness.clock.at(int(migration.expiry - harness.clock.origin.timestamp()))
    assert harness.client.cookies.get("session_id") == migration.token
    harness.response = harness.client.get("/welcome")
    assert harness.services.sessions.get(migration.token) is None


@given("隔離 SQLite 中已有一筆到期時間已過的會員 Session")
def expired_source_session(migration: MigrationSnapshot) -> None:
    migration.member()
    migration.session(expired=True)


@then("目標保留該 Session 記錄及原本的到期時間")
def preserved_expired(migration: MigrationSnapshot) -> None:
    migration.assert_all_rows()
    expired_rows(migration)


@when("使用該 Session 的瀏覽器存取 Welcome 頁面")
def expired_cookie(migration: MigrationSnapshot) -> None:
    original_cookie(migration)


@given("隔離 SQLite 來源與隔離 MariaDB 目標存在同名會員")
def conflicting_member(migration: MigrationSnapshot) -> None:
    migration.member(2)
    migration.harness.seed(failures=1)
    assert migration.harness.hash != migration.original_hash


@given("已記錄目標既有會員的資料內容")
def record_target(migration: MigrationSnapshot) -> None:
    migration.target_before = migration.raw_target()
    assert any(migration.target_before.values())


@when("請求將來源會員資料遷移至目標")
def conflicting_migration(migration: MigrationSnapshot) -> None:
    migration.run(conflict=True)


@then("系統回報目標資料衝突")
def conflict_reported(migration: MigrationSnapshot) -> None:
    assert migration.conflict


@then("目標既有會員的資料內容未被刪除或覆寫")
def target_unchanged(migration: MigrationSnapshot) -> None:
    actual = migration.raw_target()
    assert set(actual) == set(migration.target_before)
    for table, rows in migration.target_before.items():
        assert sorted(actual[table], key=repr) == sorted(rows, key=repr), table
    assert migration.harness.state().failed_attempts == 1
    assert migration.harness.services.members.get(
        migration.harness.username).password_hash == migration.harness.hash
