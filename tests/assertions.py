"""Bounded checks for the two reviewed test gaps; not a security proof."""

from __future__ import annotations

import base64
import binascii
import json
from typing import Any
from urllib.parse import unquote


def assert_cookie_has_no_sensitive_data(value: str, sensitive: tuple[str, ...]) -> None:
    """Inspect raw/URL/Base64/Base64URL/hex/JSON text, up to four decoding layers.

    Include dot-separated payloads (e.g. JWT); do not prescribe an ID format.
    Opaque ciphertext, custom encodings and ID generation require code review.
    """
    pending = {value}
    seen: set[str] = set()
    for _ in range(5):  # Raw value plus at most four decoding layers.
        following: set[str] = set()
        for candidate in pending - seen:
            seen.add(candidate)
            assert not any(secret and secret in candidate for secret in sensitive), (
                "Cookie contains sensitive test data (raw or reversibly encoded)"
            )
            if len(candidate) > 65536:
                continue  # Bound decoding work; this is not an ID-length requirement.
            following.add(unquote(candidate))
            if "." in candidate:
                following.update(candidate.split("."))
            try:
                parsed = json.loads(candidate)
                following.add(json.dumps(parsed, ensure_ascii=False))
            except (ValueError, RecursionError):
                pass
            for altchars in (None, b"-_"):
                try:
                    decoded = base64.b64decode(candidate + "=" * (-len(candidate) % 4),
                                               altchars=altchars, validate=True)
                    following.add(decoded.decode("utf-8"))
                except (ValueError, UnicodeError, binascii.Error):
                    pass
            try:
                following.add(bytes.fromhex(candidate).decode("utf-8"))
            except (ValueError, UnicodeError):
                pass
        pending = following


def assert_visible_message(locator: Any, expected: str | None = None) -> None:
    """Use the real browser layout; raw HTML presence is insufficient."""
    from playwright.sync_api import expect

    expect(locator).to_have_count(1)
    expect(locator).to_be_visible()
    if expected is not None:
        expect(locator).to_have_text(expected)
    else:
        assert locator.inner_text().strip(), "Visible message must not be empty"
