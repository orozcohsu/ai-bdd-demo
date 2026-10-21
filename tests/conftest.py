from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from tests.support import Harness

pytest_plugins = ["tests.bdd.steps"]


def pytest_configure(config: pytest.Config) -> None:
    for number in range(1, 8):
        config.addinivalue_line("markers", f"AUTH-{number:03}: approved Feature identifier")


@pytest.fixture
def harness(tmp_path: Path) -> Iterator[Harness]:
    value = Harness(tmp_path / "isolated.sqlite3")
    try:
        value.start()
        yield value
    finally:
        value.close()


@pytest.fixture
def ui(harness: Harness) -> Iterator[Any]:
    """Real Chromium against real app. Missing browser is an error, never a skip."""
    import uvicorn
    from playwright.sync_api import sync_playwright

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        port = listener.getsockname()[1]
        # Harness already owns lifespan; browser serves that same initialized app.
        server = uvicorn.Server(uvicorn.Config(harness.app, lifespan="off", log_level="warning"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started and thread.is_alive() and time.monotonic() < deadline:
                time.sleep(0.01)  # Infrastructure readiness, never lockout waiting.
            assert server.started, "Loopback application server failed to start"
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                try:
                    context = browser.new_context()
                    page = context.new_page()
                    page.goto(f"http://127.0.0.1:{port}/login")
                    yield page
                finally:
                    browser.close()
        finally:
            server.should_exit = True
            thread.join(timeout=10)
            assert not thread.is_alive(), "Loopback server did not stop"
