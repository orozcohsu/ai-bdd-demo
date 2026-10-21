"""Explicit approved Scenario bindings; Examples expand through pytest-bdd."""

from pytest_bdd import scenario


@scenario("AUTH-004-welcome-access.feature", "登入成功後顯示歡迎訊息")
def test_welcome_message() -> None:
    """AUTH-004: 登入成功後顯示歡迎訊息."""

@scenario("AUTH-004-welcome-access.feature", "成功登入後維持登入狀態以存取 Welcome 頁面")
def test_session_access() -> None:
    """AUTH-004: 成功登入後維持登入狀態以存取 Welcome 頁面."""

@scenario("AUTH-004-welcome-access.feature", "未登入的使用者直接存取 Welcome 頁面")
def test_anonymous_access() -> None:
    """AUTH-004: 未登入的使用者直接存取 Welcome 頁面."""

@scenario("AUTH-004-welcome-access.feature", "登入失敗後仍不得直接存取 Welcome 頁面")
def test_failed_login_access() -> None:
    """AUTH-004: 登入失敗後仍不得直接存取 Welcome 頁面."""
