"""Explicit approved Scenario bindings; Examples expand through pytest-bdd."""

from pytest_bdd import scenario


@scenario("AUTH-001-login.feature", "登入首頁提供登入表單")
def test_form() -> None:
    """AUTH-001: 登入首頁提供登入表單."""

@scenario("AUTH-001-login.feature", "重設清空帳號與密碼並將鍵盤輸入焦點移至帳號欄")
def test_reset() -> None:
    """AUTH-001: 重設清空帳號與密碼並將鍵盤輸入焦點移至帳號欄."""

@scenario("AUTH-001-login.feature", "正確的帳號與密碼可成功登入")
def test_valid_login() -> None:
    """AUTH-001: 正確的帳號與密碼可成功登入."""

@scenario("AUTH-001-login.feature", "既有帳號第一次輸入錯誤密碼")
def test_invalid_login() -> None:
    """AUTH-001: 既有帳號第一次輸入錯誤密碼."""

@scenario("AUTH-001-login.feature", "不存在的帳號顯示相同的驗證失敗訊息")
def test_missing_account() -> None:
    """AUTH-001: 不存在的帳號顯示相同的驗證失敗訊息."""

@scenario("AUTH-001-login.feature", "不存在帳號重複登入不適用既有會員鎖定規則")
def test_repeat_missing() -> None:
    """AUTH-001: 不存在帳號重複登入不適用既有會員鎖定規則."""

@scenario("AUTH-001-login.feature", "成功登入重設連續失敗次數")
def test_reset_counter() -> None:
    """AUTH-001: 成功登入重設連續失敗次數."""
