"""Step assertions exercise real routes/services, not a model of business behavior."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from http.cookies import SimpleCookie
from threading import Barrier
from typing import Any
from urllib.parse import urlsplit

import pytest
from argon2 import PasswordHasher
from pytest_bdd import given, parsers, then, when

from tests.assertions import assert_cookie_has_no_sensitive_data, assert_visible_message
from tests.support import ERROR, LOCKED, PASSWORD, WRONG, Document, Harness


@given("使用者尚未登入")
def anonymous(harness: Harness) -> None:
    assert not harness.authenticated_sessions()


@given("使用者位於登入首頁")
@when("使用者開啟登入首頁")
@when("使用者請求登入首頁")
def login_page(harness: Harness) -> None:
    harness.response = harness.client.get("/login")
    assert harness.response.status_code == 200


@given("存在一個未鎖定的會員帳號")
@given("隔離測試環境中有一個已建立的會員帳號")
def member(harness: Harness) -> None:
    harness.seed()


@given(parsers.parse("存在一個未鎖定且連續登入失敗次數為 {count:d} 的會員帳號"))
@given(parsers.parse("隔離測試環境中有一個未鎖定且連續登入失敗次數為 {count:d} 的會員帳號"))
@given(parsers.parse("一個未鎖定的會員帳號連續登入失敗次數為 {count:d}"))
def member_failures(harness: Harness, count: int) -> None:
    harness.seed(failures=count)


@given("使用者輸入的帳號不存在")
def missing_member(harness: Harness) -> None:
    harness.username = "absent-member"
    assert harness.services.members.get(harness.username) is None


@given("一個會員帳號已在時間 T 因第三次連續登入失敗而被鎖定")
@given("隔離測試環境中一個帳號在時間 T 因第三次連續失敗被鎖定")
@given("一個會員帳號仍在伺服器判定的鎖定期間")
def locked_member(harness: Harness) -> None:
    harness.seed(failures=3)
    assert harness.state().locked_until == harness.clock.origin + timedelta(seconds=60)


@given("會員帳號 A 與 B 均未鎖定且連續登入失敗次數均為 0")
def two_members(harness: Harness) -> None:
    harness.seed("member-a")
    harness.seed("member-b")


@given("會員帳號 A 已被鎖定且仍在鎖定期間")
def locked_a(harness: Harness) -> None:
    harness.seed("member-a", failures=3)


@given("會員帳號 B 未鎖定且連續登入失敗次數為 0")
def member_b(harness: Harness) -> None:
    harness.seed("member-b")


@given("使用者已成功登入且登入狀態仍有效")
def authenticated(harness: Harness) -> None:
    harness.seed()
    harness.login()
    harness.assert_success()


@given("隔離測試環境使用 HTTPS")
def https(harness: Harness) -> None:
    harness.close()
    harness.settings = replace(harness.settings, cookie_secure=True)
    harness.start()


@when("使用者透過登入表單提交該帳號與正確密碼")
@when("使用者以該帳號與正確密碼登入")
def correct_login(harness: Harness) -> None:
    harness.login()


@when("使用者透過登入表單提交該帳號與錯誤密碼")
@when("使用者以該帳號與錯誤密碼登入")
@when("該帳號在時間 T 以錯誤密碼登入")
@when("該帳號再送出 1 個錯誤密碼登入請求")
def wrong_login(harness: Harness) -> None:
    harness.login(WRONG)


@when("該帳號接著發生一次錯誤密碼登入嘗試")
def wrong_after_success(harness: Harness) -> None:
    harness.fresh_client()
    harness.login(WRONG)


@when("使用者透過登入表單首次提交該帳號與密碼")
def missing_login(harness: Harness) -> None:
    harness.login()


@when(parsers.parse("使用者對該不存在帳號連續提交 {count:d} 次登入請求"))
def repeat_missing(harness: Harness, count: int) -> None:
    harness.responses = [harness.login() for _ in range(count)]
    assert len(harness.responses) == count


@when(parsers.parse("該帳號在時間 T 後 {seconds:d} 秒以{kind}登入"))
def timed_login(harness: Harness, seconds: int, kind: str) -> None:
    assert kind in {"正確密碼", "錯誤密碼"}
    harness.clock.at(seconds)
    harness.login(PASSWORD if kind == "正確密碼" else WRONG)


@when(parsers.parse("時間到達 T 後 {seconds:d} 秒且期間沒有其他登入嘗試"))
def advance(harness: Harness, seconds: int) -> None:
    harness.clock.at(seconds)


@when(parsers.parse("帳號 A 連續發生 {count:d} 次錯誤密碼登入嘗試"))
def fail_a(harness: Harness, count: int) -> None:
    for _ in range(count):
        harness.login(WRONG, "member-a")
        harness.assert_rejected()


@when("帳號 B 發生 1 次錯誤密碼登入嘗試")
def fail_b(harness: Harness) -> None:
    harness.login(WRONG, "member-b")
    harness.assert_rejected()


@when("使用者以帳號 B 與正確密碼登入")
def login_b(harness: Harness) -> None:
    harness.username = "member-b"
    harness.login()


@then("系統成功驗證會員")
@then("系統建立該會員的登入狀態")
@then("系統允許登入")
@then("系統允許帳號 B 登入")
@then("登入狀態由伺服器端 Session 管理")
def success(harness: Harness) -> None:
    harness.assert_success()


@then("系統導向 Welcome 頁面")
def redirect_welcome(harness: Harness) -> None:
    harness.assert_success()
    harness.welcome(harness.client.get("/welcome").text)


@then("系統拒絕登入")
def rejected(harness: Harness) -> None:
    harness.assert_rejected()


@then(parsers.parse("登入頁面顯示「{message}」"))
def alert(harness: Harness, message: str) -> None:
    harness.alert(message)


@then("頁面不顯示專屬的「帳號不存在」訊息")
def no_enumeration(harness: Harness) -> None:
    assert "帳號不存在" not in harness.response.text


@then("每次請求均被拒絕登入")
def all_rejected(harness: Harness) -> None:
    assert harness.responses
    for response in harness.responses:
        harness.assert_rejected(response)


@then("每次登入回應均顯示「帳號或密碼錯誤」")
def all_errors(harness: Harness) -> None:
    assert harness.responses
    for response in harness.responses:
        harness.alert(ERROR, response)


@then("每次登入回應均不顯示鎖定提示")
def no_lock_message(harness: Harness) -> None:
    assert harness.responses
    assert all(LOCKED not in r.text for r in harness.responses)


@then("每次登入回應均不顯示專屬的「帳號不存在」訊息")
def no_missing_message(harness: Harness) -> None:
    assert harness.responses
    assert all("帳號不存在" not in r.text for r in harness.responses)


@then(parsers.parse("該帳號的連續登入失敗次數為 {count:d}"))
def count(harness: Harness, count: int) -> None:
    assert harness.state().failed_attempts == count


@then(parsers.parse("帳號 {account} 的連續登入失敗次數為 {count:d}"))
def named_count(harness: Harness, account: str, count: int) -> None:
    assert account in {"A", "B"}
    assert harness.state(f"member-{account.lower()}").failed_attempts == count


@then("該帳號未被鎖定")
@then("該帳號已自動解除鎖定")
def unlocked(harness: Harness) -> None:
    assert not harness.state().is_locked


@then("該帳號立即被鎖定")
def is_locked(harness: Harness) -> None:
    assert harness.state().is_locked
    # Also prove enforcement externally, rather than trust the state getter alone.
    original_response, original_client = harness.response, harness.client
    harness.fresh_client()
    try:
        response = harness.login(PASSWORD)
        harness.assert_rejected(response)
        harness.alert(LOCKED, response)
    finally:
        harness.response, harness.client = original_response, original_client


@then("鎖定期間從時間 T 開始持續 60 秒")
def lock_deadline(harness: Harness) -> None:
    assert harness.state().locked_until == harness.clock.origin + timedelta(seconds=60)


@then("帳號 A 與 B 均未被鎖定")
def both_unlocked(harness: Harness) -> None:
    assert not harness.state("member-a").is_locked
    assert not harness.state("member-b").is_locked


@then("帳號 A 仍維持原鎖定狀態")
def a_still_locked(harness: Harness) -> None:
    state = harness.state("member-a")
    assert state.is_locked
    assert state.locked_until == harness.clock.origin + timedelta(seconds=60)
    harness.fresh_client()
    harness.login(PASSWORD, "member-a")
    harness.assert_rejected()
    harness.alert(LOCKED)


@when("使用者再次存取 Welcome 頁面")
@when("使用者直接存取 Welcome 頁面")
@when("使用者請求 Welcome 頁面")
def request_welcome(harness: Harness) -> None:
    harness.response = harness.client.get("/welcome")


@then("系統允許存取 Welcome 頁面")
def allowed_welcome(harness: Harness) -> None:
    assert harness.response.status_code == 200


@then("系統不允許存取 Welcome 頁面")
@then("系統導向登入首頁")
def denied_welcome(harness: Harness) -> None:
    assert harness.response.status_code == 303
    assert urlsplit(harness.response.headers["location"]).path == "/login"


@then("Welcome 頁面顯示歡迎訊息")
def welcome_message(harness: Harness, ui: Any) -> None:
    response = harness.client.get("/welcome")
    assert response.status_code == 200
    harness.welcome(response.text)
    # Transfer the actual valid session to the loopback browser, preserving its value.
    cookie, _ = harness.authenticated_sessions()[0]
    ui.context.add_cookies([{"name": cookie.name, "value": cookie.value, "url": ui.url}])
    ui.goto(ui.url.replace("/login", "/welcome"))
    assert_visible_message(ui.get_by_test_id("welcome-message"))


@then("伺服器回應的 HTML 包含歡迎訊息")
def ssr_welcome(harness: Harness) -> None:
    assert harness.response.status_code == 200
    harness.welcome(harness.response.text)


@then("頁面提供帳號輸入欄位")
@then("頁面提供密碼輸入欄位")
@then("伺服器回應的 HTML 包含帳號與密碼輸入欄位")
def form_fields(harness: Harness) -> None:
    doc = Document(harness.response.text)
    for name in ("username", "password"):
        assert doc.field(name).attrs.get("id") == name
        assert any(e.text.strip() for e in doc.find("label", **{"for": name}))
    assert doc.field("password").attrs.get("type") == "password"
    forms = doc.find("form")
    assert any(e.attrs.get("method", "get").lower() == "post"
               and e.attrs.get("action") == "/login" for e in forms)


@then("頁面提供登入按鈕")
@then("伺服器回應的 HTML 包含登入按鈕")
def submit_button(harness: Harness) -> None:
    assert Document(harness.response.text).button("登入").attrs.get("type") == "submit"


@then("頁面提供重設按鈕")
def reset_button(harness: Harness) -> None:
    assert Document(harness.response.text).button("重設").attrs.get("type") in {"button", "reset"}


@given(parsers.re(r"帳號欄位目前為「(?P<value>.*)」"))
def fill_username(ui: Any, value: str) -> None:
    ui.locator("#username").fill(value)


@given(parsers.re(r"密碼欄位目前為「(?P<value>.*)」"))
def fill_password(ui: Any, value: str) -> None:
    ui.locator("#password").fill(value)


@when("使用者按下重設按鈕")
def reset(ui: Any) -> None:
    requests: list[str] = []
    ui.on("request", lambda request: requests.append(request.method))
    ui.get_by_role("button", name="重設", exact=True).click()
    # Allow the browser to finish the click before inspecting for an unwanted submit.
    ui.evaluate("() => new Promise(resolve => requestAnimationFrame(resolve))")
    assert "POST" not in requests


@then("帳號欄位內容為空")
def username_empty(ui: Any) -> None:
    assert ui.locator("#username").input_value() == ""


@then("密碼欄位內容為空")
@then("密碼欄位內容仍為空")
def password_empty(ui: Any) -> None:
    assert ui.locator("#password").input_value() == ""


@then("帳號欄位取得鍵盤輸入焦點")
def focused(ui: Any) -> None:
    assert ui.locator("#username").evaluate("element => document.activeElement === element")


@when("使用者直接以鍵盤輸入「next-member」而不重新選取欄位")
def keyboard(ui: Any) -> None:
    ui.keyboard.type("next-member")


@then("帳號欄位內容為「next-member」")
def typed_username(ui: Any) -> None:
    assert ui.locator("#username").input_value() == "next-member"


@when("使用者在密碼欄位輸入測試密碼")
def password_input(ui: Any) -> None:
    ui.locator("#password").fill(PASSWORD)


@then("密碼欄位不以明文顯示輸入內容")
def masked(ui: Any) -> None:
    assert ui.locator("#password").input_value() == PASSWORD
    assert ui.locator("#password").get_attribute("type") == "password"


@when("檢查該帳號儲存的密碼驗證資料")
def read_hash(harness: Harness) -> None:
    record = harness.services.members.get(harness.username)
    assert record is not None
    harness.hash = record.password_hash


@then("資料不包含明文密碼")
def no_plaintext(harness: Harness) -> None:
    assert PASSWORD not in harness.hash


@then("密碼驗證資料使用安全的密碼雜湊演算法")
def real_hash(harness: Harness) -> None:
    # The test seeded a real Argon2 hash; verify the persisted credential actually works.
    assert PasswordHasher().verify(harness.hash, PASSWORD)
    harness.login()
    harness.assert_success()


@when(parsers.parse("使用者以該帳號及{kind}進行登入"))
def logged_login(harness: Harness, kind: str, caplog: pytest.LogCaptureFixture) -> None:
    assert kind in {"正確密碼", "錯誤密碼"}
    caplog.clear()
    caplog.set_level("DEBUG")
    harness.login(PASSWORD if kind == "正確密碼" else WRONG)
    if kind == "正確密碼":
        harness.assert_success()
    else:
        harness.assert_rejected()


@then("本次處理產生的日誌不包含輸入的明文密碼")
def safe_logs(harness: Harness, caplog: pytest.LogCaptureFixture) -> None:
    assert harness.last_password not in caplog.text


@then("瀏覽器僅保存不含敏感資料的 Session ID 作為登入憑證")
def opaque_session(harness: Harness) -> None:
    harness.assert_success()
    cookie, record = harness.authenticated_sessions()[0]
    assert_cookie_has_no_sensitive_data(
        cookie.value, (PASSWORD, harness.username, harness.hash, harness.settings.secret_key),
    )
    assert record.username == harness.username
    # A copied opaque ID grants access, while an altered ID does not.
    original = harness.client
    client = harness.fresh_client()
    client.cookies.set(cookie.name, cookie.value)
    assert client.get("/welcome").status_code == 200
    client.cookies.set(cookie.name, cookie.value + "tampered")
    assert client.get("/welcome").status_code == 303
    harness.client = original


@then(parsers.parse("Session Cookie 設定 {attribute}"))
def cookie_attribute(harness: Harness, attribute: str) -> None:
    cookie, _ = harness.authenticated_sessions()[0]
    parsed = SimpleCookie()
    for header in harness.response.headers.get_list("set-cookie"):
        parsed.load(header)
    assert cookie.name in parsed
    morsel = parsed[cookie.name]
    assert attribute in {"HttpOnly", "SameSite", "Secure"}
    assert morsel[attribute.lower()]
    if attribute == "SameSite":
        assert morsel["samesite"].lower() == harness.settings.cookie_samesite


@when("使用者提交正確帳號與密碼但未提供有效的 CSRF 證明")
def invalid_csrf(harness: Harness) -> None:
    harness.form()
    harness.response = harness.client.post("/login", data={"username": harness.username,
                                                         "password": PASSWORD})


@then("系統不接受該請求完成登入")
@then("系統不建立該請求的登入狀態")
def csrf_rejected(harness: Harness) -> None:
    assert harness.response.status_code == 403
    assert not harness.authenticated_sessions()
    assert harness.client.get("/welcome").status_code == 303


@given("登入處理過程發生可控制的內部系統錯誤")
def controlled_error(harness: Harness, monkeypatch: pytest.MonkeyPatch) -> None:
    harness.seed()

    def fail(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError(f"INTERNAL-TEST-MARKER {harness.settings.secret_key}")

    monkeypatch.setattr(harness.services.members, "get", fail)


@when("系統回應使用者的登入請求")
def error_request(harness: Harness) -> None:
    harness.login()
    assert 500 <= harness.response.status_code < 600, "Fault must reach real error handling"


@then("回應不包含機密資訊")
def safe_error(harness: Harness) -> None:
    assert harness.settings.secret_key not in harness.response.text
    assert PASSWORD not in harness.response.text


@then("回應不包含詳細系統錯誤")
def generic_error(harness: Harness) -> None:
    assert harness.response.text.strip()
    for detail in ("INTERNAL-TEST-MARKER", "Traceback", "RuntimeError", "File \""):
        assert detail not in harness.response.text


@when("應用程式重新啟動並使用原本的隔離 SQLite 資料庫")
def restart(harness: Harness) -> None:
    harness.restart()


@when("應用程式在時間 T 後 30 秒重新啟動並使用原本的隔離 SQLite 資料庫")
def timed_restart(harness: Harness) -> None:
    harness.clock.at(30)
    harness.restart()


@when("使用者以未保存該帳號本地狀態的新瀏覽器提交正確帳號與密碼")
def clean_browser(harness: Harness, ui: Any) -> None:
    # ui is a new real Chromium context; it has never visited this account.
    ui.locator("#username").fill(harness.username)
    ui.locator("#password").fill(PASSWORD)
    with ui.expect_response(lambda r: r.request.method == "POST"
                            and urlsplit(r.url).path == "/login") as result:
        ui.get_by_role("button", name="登入", exact=True).click()
    response = result.value
    # Preserve the actual server response for common rejection/message assertions.
    import httpx

    harness.response = httpx.Response(response.status, text=response.text())
    assert ui.request.get(ui.url.replace("/login", "/welcome"),
                          max_redirects=0).status == 303


@when("該帳號同時送出 2 個錯誤密碼登入請求且均處理完成")
def concurrent_failures(harness: Harness) -> None:
    from starlette.testclient import TestClient

    barrier = Barrier(2)

    def attempt(_: int) -> Any:
        client = TestClient(harness.app, follow_redirects=False,
                            raise_server_exceptions=False)
        try:
            token = harness.form(client)
            barrier.wait(timeout=10)
            response = client.post("/login", data={"username": harness.username,
                                                   "password": WRONG, "csrf_token": token})
            harness.assert_rejected(response, client)
            harness.alert(ERROR, response)
            return response
        finally:
            client.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        harness.responses = list(pool.map(attempt, range(2)))
