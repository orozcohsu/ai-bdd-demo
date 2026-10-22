"""Local assertion regressions only: no fake application or product PASS evidence."""

import base64
import json
from collections.abc import Iterator
from typing import Any
from urllib.parse import quote

import pytest

from tests.assertions import assert_cookie_has_no_sensitive_data, assert_visible_message

SECRET = "assertion-only-password!"
PAYLOAD = json.dumps({"password": SECRET})
ENCODED = base64.urlsafe_b64encode(PAYLOAD.encode()).decode().rstrip("=")


@pytest.mark.parametrize("value", [
    PAYLOAD, quote(PAYLOAD, safe=""), ENCODED,
    base64.b64encode(PAYLOAD.encode()).decode(), PAYLOAD.encode().hex(),
    f"header.{ENCODED}.signature", PAYLOAD.replace("!", r"\u0021"),
    base64.b64encode(ENCODED.encode()).decode(),
])
def test_encoded_sensitive_cookie_is_rejected(value: str) -> None:
    with pytest.raises(AssertionError, match="sensitive test data"):
        assert_cookie_has_no_sensitive_data(value, (SECRET,))


def test_opaque_cookie_is_not_rejected_for_its_format() -> None:
    assert_cookie_has_no_sensitive_data("opaque-session-91df384b", (SECRET,))


@pytest.fixture
def assertion_page() -> Iterator[Any]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.set_default_timeout(200)
            yield page
        finally:
            browser.close()


@pytest.mark.parametrize("attributes", ["hidden", 'style="display:none"',
                                      'style="visibility:hidden"'])
@pytest.mark.parametrize("selector", ['[data-testid="welcome-message"]', '[role="alert"]'])
def test_hidden_message_is_rejected(assertion_page: Any, attributes: str, selector: str) -> None:
    assertion_page.set_content(
        f'<div data-testid="welcome-message" role="alert" {attributes}>Message</div>'
    )
    with pytest.raises(AssertionError):
        assert_visible_message(assertion_page.locator(selector), "Message")


def test_visible_message_is_accepted(assertion_page: Any) -> None:
    assertion_page.set_content('<div data-testid="welcome-message">Message</div>')
    assert_visible_message(assertion_page.get_by_test_id("welcome-message"), "Message")
