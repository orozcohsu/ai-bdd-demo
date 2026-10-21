"""Explicit approved Scenario bindings; Examples expand through pytest-bdd."""

from pytest_bdd import scenario


@scenario("AUTH-002-account-lockout.feature", "前兩次連續失敗只累計次數而不鎖定")
def test_first_two_failures() -> None:
    """AUTH-002: 前兩次連續失敗只累計次數而不鎖定."""

@scenario("AUTH-002-account-lockout.feature", "第三次連續失敗立即鎖定六十秒")
def test_third_failure() -> None:
    """AUTH-002: 第三次連續失敗立即鎖定六十秒."""

@scenario("AUTH-002-account-lockout.feature", "鎖定期間無論密碼是否正確均拒絕登入")
def test_locked_passwords() -> None:
    """AUTH-002: 鎖定期間無論密碼是否正確均拒絕登入."""

@scenario("AUTH-002-account-lockout.feature", "鎖定期間的登入嘗試不延長原鎖定期限")
def test_fixed_deadline() -> None:
    """AUTH-002: 鎖定期間的登入嘗試不延長原鎖定期限."""

@scenario("AUTH-002-account-lockout.feature", "不同帳號的失敗次數分別計算")
def test_separate_counts() -> None:
    """AUTH-002: 不同帳號的失敗次數分別計算."""

@scenario("AUTH-002-account-lockout.feature", "一個帳號被鎖定不影響另一帳號登入")
def test_separate_locks() -> None:
    """AUTH-002: 一個帳號被鎖定不影響另一帳號登入."""
