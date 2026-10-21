"""Integration checks for approved settings/lifespan/Session contracts."""

from datetime import timedelta
from pathlib import Path

from tests.support import PASSWORD, Harness


def test_independent_sqlite_applications(harness: Harness, tmp_path: Path) -> None:
    """A member/session in one configured database must not leak into another."""
    harness.seed()
    harness.login()
    harness.assert_success()
    other = Harness(tmp_path / "other.sqlite3")
    try:
        other.start()
        assert other.services.members.get(harness.username) is None
        other.login(PASSWORD, harness.username)
        other.assert_rejected()
        assert harness.settings.database_path != other.settings.database_path
        assert harness.settings.database_path.is_file()
        assert other.settings.database_path.is_file()
        assert harness.client.get("/welcome").status_code == 200
    finally:
        other.close()


def test_configured_session_expiry(harness: Harness) -> None:
    """The test TTL controls both server record validity and protected HTTP access."""
    harness.seed()
    harness.login()
    harness.assert_success()
    cookie, record = harness.authenticated_sessions()[0]
    ttl = harness.settings.session_ttl_seconds
    assert record.expires_at == harness.clock.origin + timedelta(seconds=ttl)
    harness.clock.at(ttl - 1)
    assert harness.client.get("/welcome").status_code == 200
    harness.clock.at(ttl)
    assert harness.services.sessions.get(cookie.value) is None
    response = harness.client.get("/welcome")
    assert response.status_code == 303
    assert response.headers["location"].endswith("/login")


def test_invalid_csrf_value_does_not_authenticate(harness: Harness) -> None:
    """Complement the missing-token BDD case with an actually invalid token."""
    harness.seed()
    token = harness.form()
    harness.response = harness.client.post("/login", data={
        "username": harness.username, "password": PASSWORD, "csrf_token": token + "invalid",
    })
    assert harness.response.status_code == 403
    assert not harness.authenticated_sessions()
    assert harness.client.get("/welcome").status_code == 303
