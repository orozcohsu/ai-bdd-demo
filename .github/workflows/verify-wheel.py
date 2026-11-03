"""Run with the wheel-only interpreter from outside the checkout; no tests/src imports."""

import importlib
import json
import os
import secrets
from importlib.resources import files
from pathlib import Path

from argon2 import PasswordHasher
from starlette.testclient import TestClient

import ai_bdd_demo
from ai_bdd_demo.config import AppSettings
from ai_bdd_demo.db import initialize_schema
from ai_bdd_demo.main import create_app


def main():
    checkout = Path(os.environ["GITHUB_WORKSPACE"]).resolve()
    package_path = Path(ai_bdd_demo.__file__).resolve()
    if package_path.is_relative_to(checkout):
        raise RuntimeError("Wheel verification imported checkout code")
    if os.environ["AI_BDD_TEST_DB_HOST"] != "127.0.0.1":
        raise RuntimeError("Wheel check requires disposable loopback service")
    driver = importlib.import_module("pymysql")

    def connect(database=None):
        connection = driver.connect(
            host="127.0.0.1", port=int(os.environ["AI_BDD_TEST_DB_PORT"]),
            user=os.environ["AI_BDD_TEST_DB_USER"], password=os.environ["AI_BDD_TEST_DB_PASSWORD"],
            database=database, autocommit=True, connect_timeout=5,
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION(), @@server_id")
            version, server_id = cursor.fetchone()
            if (not str(version).startswith("11.8.6-MariaDB")
                    or int(server_id) != int(os.environ["AI_BDD_TEST_DB_SERVER_ID"])):
                connection.close()
                raise RuntimeError("Wheel database service identity mismatch")
        return connection

    name = "bdd_test_" + secrets.token_hex(16)
    owner = secrets.token_hex(32)
    marker_ready = False
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE `{name}`")
    try:
        with connect(name) as connection, connection.cursor() as cursor:
            cursor.execute("CREATE TABLE _bdd_test_owner (token VARCHAR(64) NOT NULL)")
            cursor.execute("INSERT INTO _bdd_test_owner VALUES (%s)", (owner,))
        marker_ready = True
        settings = AppSettings(
            db_host="127.0.0.1", db_port=int(os.environ["AI_BDD_TEST_DB_PORT"]), db_name=name,
            db_user=os.environ["AI_BDD_TEST_DB_USER"], db_password=os.environ["AI_BDD_TEST_DB_PASSWORD"],
            secret_key=secrets.token_urlsafe(32), cookie_secure=False,
            session_ttl_seconds=300, cookie_samesite="lax",
        )
        initialize_schema(settings=settings)
        package = files("ai_bdd_demo")
        resources = ("templates/login.html", "templates/welcome.html",
                     "static/style.css", "static/login.js")
        for resource in resources:
            if not package.joinpath(resource).is_file():
                raise RuntimeError(f"Missing wheel resource: {resource}")
        app = create_app(settings=settings)
        with TestClient(app, follow_redirects=False) as client:
            password = secrets.token_urlsafe(24)
            app.state.services.members.create("wheel-member", PasswordHasher().hash(password))
            response = client.get("/login")
            assert response.status_code == 200 and 'name="username"' in response.text
            for path in ("/static/style.css", "/static/login.js"):
                assert client.get(path).status_code == 200
            response = client.post("/login", data={"username": "wheel-member", "password": password,
                                                  "csrf_token": client.cookies.get("csrf_proof")})
            assert response.status_code == 303 and response.headers["location"].endswith("/welcome")
            response = client.get("/welcome")
            assert response.status_code == 200 and "welcome-message" in response.text
        Path(os.environ["WHEEL_REPORT"]).write_text(json.dumps({
            "result": "PASS", "imported_package": str(package_path), "database": name,
            "resources": list(resources), "login": "PASS", "welcome": "PASS", "static": "PASS",
        }, indent=2), encoding="utf-8")
        print("Installed wheel: real MariaDB application, login, welcome and resources PASS")
    finally:
        if not marker_ready:
            raise RuntimeError("Ownership setup incomplete; database retained for inspection")
        with connect(name) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT token FROM _bdd_test_owner")
            if cursor.fetchall() != ((owner,),):
                raise RuntimeError("Refusing wheel database cleanup: ownership mismatch")
        with connect() as connection, connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE `{name}`")


if __name__ == "__main__":
    main()
