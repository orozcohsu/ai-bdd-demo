"""Test-infrastructure safety checks; these are not product/MariaDB acceptance evidence."""

import pytest

from tests.mariadb_support import MariaDBServer, TestSettings


def test_missing_configuration_never_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("HOST", "PORT", "USER", "PASSWORD", "SERVER_ID", "DISPOSABLE"):
        monkeypatch.delenv(f"AI_BDD_TEST_DB_{key}", raising=False)
    with pytest.raises(RuntimeError, match="no production/SQLite fallback"):
        MariaDBServer()


def test_public_host_rejected_before_connect(monkeypatch: pytest.MonkeyPatch) -> None:
    for key, value in {"HOST": "192.0.2.1", "PORT": "3306", "USER": "test-only",
                       "PASSWORD": "guard-test-only", "SERVER_ID": "17",
                       "DISPOSABLE": "YES"}.items():
        monkeypatch.setenv(f"AI_BDD_TEST_DB_{key}", value)
    with pytest.raises(RuntimeError, match="Only loopback"):
        MariaDBServer()


@pytest.mark.parametrize("name,token", [
    ("bdd", "owned"),
    ("bdd_test_not_a_case", "owned"),
    ("bdd_test_" + "a" * 32, "wrong-token"),
])
def test_unowned_cleanup_rejected_without_connection(name: str, token: str) -> None:
    # Only exercise the local cleanup guard. No database/production SUT is mocked.
    server = MariaDBServer.__new__(MariaDBServer)
    server.owned = {"bdd_test_" + "a" * 32: "owned"}
    with pytest.raises(RuntimeError, match="not owned"):
        server.drop_owned(name, token)


def test_settings_repr_excludes_secrets() -> None:
    settings = TestSettings("localhost", 13306, "bdd_test_" + "a" * 32, "test-only",
                            "private-db-test-value", "private-secret-test-value")
    assert "private-db-test-value" not in repr(settings)
    assert "private-secret-test-value" not in repr(settings)
