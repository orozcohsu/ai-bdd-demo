"""Explicit approved Scenario bindings; Examples expand through pytest-bdd."""

from pytest_bdd import scenario


@scenario("AUTH-007-login-presentation.feature", "登入首頁回應包含伺服器產生的表單 HTML")
def test_ssr_login() -> None:
    """AUTH-007: 登入首頁回應包含伺服器產生的表單 HTML."""

@scenario("AUTH-007-login-presentation.feature", "Welcome 頁回應包含伺服器產生的歡迎訊息")
def test_ssr_welcome() -> None:
    """AUTH-007: Welcome 頁回應包含伺服器產生的歡迎訊息."""
