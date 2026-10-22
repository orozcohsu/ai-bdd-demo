"""Supplement HTTP error checks with real browser visibility for both messages."""

from typing import Any

import pytest

from tests.assertions import assert_visible_message
from tests.support import ERROR, LOCKED, WRONG, Harness


@pytest.mark.parametrize(("failures", "message"), [(0, ERROR), (2, LOCKED)])
def test_login_error_is_visible(harness: Harness, ui: Any, failures: int, message: str) -> None:
    harness.seed(failures=failures)
    ui.locator("#username").fill(harness.username)
    ui.locator("#password").fill(WRONG)
    with ui.expect_response(lambda r: r.request.method == "POST" and "/login" in r.url):
        ui.get_by_role("button", name="登入", exact=True).click()
    assert_visible_message(ui.get_by_role("alert"), message)
    denied = ui.request.get(ui.url.replace("/login", "/welcome"), max_redirects=0)
    assert denied.status == 303
