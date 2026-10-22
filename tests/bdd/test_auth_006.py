"""Explicit approved Scenario bindings; Examples expand through pytest-bdd."""

from pytest_bdd import scenario


@scenario("AUTH-006-lockout-consistency.feature", "應用程式重新啟動後保留連續登入失敗次數")
def test_persist_count() -> None:
    """AUTH-006: 應用程式重新啟動後保留連續登入失敗次數."""

@scenario("AUTH-006-lockout-consistency.feature", "應用程式重新啟動後保留原鎖定期限")
def test_persist_deadline() -> None:
    """AUTH-006: 應用程式重新啟動後保留原鎖定期限."""

@scenario("AUTH-006-lockout-consistency.feature", "瀏覽器端狀態不能解除伺服器鎖定")
def test_fresh_browser() -> None:
    """AUTH-006: 瀏覽器端狀態不能解除伺服器鎖定."""

@scenario("AUTH-006-lockout-consistency.feature", "同帳號的並行失敗不遺失累計次數")
def test_concurrent_count() -> None:
    """AUTH-006: 同帳號的並行失敗不遺失累計次數."""
