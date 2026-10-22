"""Real application adapters for docs/system-standard.md, sections 2–7."""

from __future__ import annotations

import importlib
import secrets
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlsplit

from argon2 import PasswordHasher
from starlette.testclient import TestClient

PASSWORD = "isolated-valid-password-482!"
WRONG = "isolated-wrong-password-719!"
ERROR = "帳號或密碼錯誤"
LOCKED = "登入暫時受限，請於 1 分鐘後再試"


@dataclass(frozen=True)
class TestSettings:
    """Structural settings carrier: only the attributes in the approved contract."""

    __test__ = False
    database_path: Path
    secret_key: str
    cookie_secure: bool = False
    session_ttl_seconds: int = 300  # Isolated test value, not production policy.
    cookie_samesite: str = "lax"  # Isolated test value, not production policy.


class ControlledClock:
    def __init__(self) -> None:
        self.origin = datetime(2030, 1, 1, tzinfo=UTC)
        self._value = self.origin
        self._lock = Lock()

    def now(self) -> datetime:
        with self._lock:
            return self._value

    def at(self, seconds: int) -> None:
        with self._lock:
            self._value = self.origin + timedelta(seconds=seconds)


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str = ""


class Document(HTMLParser):
    """Parse server HTML using stdlib; no browser DOM is substituted for SSR."""

    def __init__(self, html: str) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[Element] = []
        self._stack: list[Element] = []
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        element = Element(tag, {key: value or "" for key, value in attrs})
        self.elements.append(element)
        if tag not in {"input", "br", "hr", "img", "meta", "link", "area", "wbr"}:
            self._stack.append(element)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._stack) - 1, -1, -1):
            if self._stack[index].tag == tag:
                del self._stack[index:]
                break

    def handle_data(self, data: str) -> None:
        for element in self._stack:
            element.text += data

    def find(self, tag: str | None = None, **attrs: str) -> list[Element]:
        return [e for e in self.elements if (tag is None or e.tag == tag)
                and all(e.attrs.get(k) == v for k, v in attrs.items())]

    def field(self, name: str) -> Element:
        fields = self.find("input", name=name)
        assert len(fields) == 1, f"Expected one input named {name}"
        return fields[0]

    def button(self, text: str) -> Element:
        buttons = [e for e in self.find("button") if e.text.strip() == text]
        buttons += [e for e in self.find("input") if e.attrs.get("value") == text
                    and e.attrs.get("type") in {"submit", "reset", "button"}]
        assert len(buttons) == 1, f"Expected one accessible button {text}"
        return buttons[0]


class Harness:
    def __init__(self, path: Path) -> None:
        self.settings = TestSettings(path.resolve(), secrets.token_urlsafe(32))
        self.clock = ControlledClock()
        self.stack = ExitStack()
        self.app: Any = None
        self.client: Any = None
        self.response: Any = None
        self.responses: list[Any] = []
        self.username = "member-a"
        self.last_password = PASSWORD
        self.hash: str = ""

    def start(self) -> None:
        try:
            module = importlib.import_module("ai_bdd_demo.main")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Application unavailable: implement/install ai_bdd_demo.main:create_app "
                "per docs/system-standard.md. This is NOT a behavioral Red."
            ) from exc
        self.app = module.create_app(settings=self.settings, clock=self.clock)
        self.client = self.stack.enter_context(TestClient(
            self.app, base_url="https://testserver" if self.settings.cookie_secure
            else "http://testserver", follow_redirects=False, raise_server_exceptions=False,
        ))

    def close(self) -> None:
        self.stack.close()

    @property
    def services(self) -> Any:
        return self.app.state.services

    def fresh_client(self) -> Any:
        # Primary client owns lifespan; these clients share the actual running app.
        self.client = TestClient(self.app, base_url=str(self.client.base_url),
                                 follow_redirects=False, raise_server_exceptions=False)
        self.stack.callback(self.client.close)
        return self.client

    def restart(self) -> None:
        self.close()
        self.stack = ExitStack()
        assert self.settings.database_path.is_file(), "SQLite must persist before restart"
        self.start()

    def seed(self, username: str = "member-a", failures: int = 0) -> None:
        self.username = username
        self.hash = PasswordHasher().hash(PASSWORD)
        self.services.members.create(username, self.hash)
        for _ in range(failures):
            response = self.login(WRONG)
            assert response.status_code == 200
        state = self.state(username)
        assert state.failed_attempts == failures
        assert bool(state.is_locked) == (failures >= 3)

    def state(self, username: str | None = None) -> Any:
        result = self.services.auth.get_account_state(username or self.username)
        assert result is not None, "Expected existing member state"
        return result

    def form(self, client: Any = None) -> str:
        response = (client or self.client).get("/login")
        assert response.status_code == 200
        token = Document(response.text).field("csrf_token")
        assert token.attrs.get("type") == "hidden"
        assert token.attrs.get("value"), "Normal requests require a real CSRF token"
        return token.attrs["value"]

    def login(self, password: str = PASSWORD, username: str | None = None,
              client: Any = None) -> Any:
        target = client or self.client
        token = self.form(target)
        self.last_password = password
        self.response = target.post("/login", data={"username": username or self.username,
                                   "password": password, "csrf_token": token})
        return self.response

    def authenticated_sessions(self) -> list[tuple[Any, Any]]:
        matches = []
        for cookie in self.client.cookies.jar:
            record = self.services.sessions.get(cookie.value)
            if record is not None:
                matches.append((cookie, record))
        return matches

    def assert_success(self) -> None:
        assert self.response.status_code == 303
        assert urlsplit(self.response.headers["location"]).path == "/welcome"
        sessions = self.authenticated_sessions()
        assert len(sessions) == 1
        assert sessions[0][1].username == self.username
        assert sessions[0][1].expires_at > self.clock.now()
        assert self.client.get("/welcome").status_code == 200

    def assert_rejected(self, response: Any = None, client: Any = None) -> None:
        response = self.response if response is None else response
        assert response.status_code == 200
        denied = (client or self.client).get("/welcome")
        assert denied.status_code == 303
        assert urlsplit(denied.headers["location"]).path == "/login"

    def alert(self, expected: str, response: Any = None) -> None:
        response = self.response if response is None else response
        alerts = Document(response.text).find(role="alert")
        assert any(e.text.strip() == expected for e in alerts), f"Missing alert: {expected}"

    def welcome(self, html: str) -> None:
        elements = Document(html).find(**{"data-testid": "welcome-message"})
        assert len(elements) == 1 and elements[0].text.strip()
