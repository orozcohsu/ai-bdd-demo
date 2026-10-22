"""Explicit approved Scenario bindings; Examples expand through pytest-bdd."""

from pytest_bdd import scenario


@scenario("AUTH-003-lockout-expiry.feature", "鎖定到期前仍拒絕正確密碼登入")
def test_before_expiry() -> None:
    """AUTH-003: 鎖定到期前仍拒絕正確密碼登入."""

@scenario("AUTH-003-lockout-expiry.feature", "鎖定滿六十秒或之後可再次登入")
def test_at_or_after_expiry() -> None:
    """AUTH-003: 鎖定滿六十秒或之後可再次登入."""

@scenario("AUTH-003-lockout-expiry.feature", "鎖定到期後的錯誤密碼從第一次失敗重新累計")
def test_failure_after_expiry() -> None:
    """AUTH-003: 鎖定到期後的錯誤密碼從第一次失敗重新累計."""
