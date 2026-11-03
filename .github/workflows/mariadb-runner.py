"""Owned, loopback-only MariaDB container for a single GitHub-hosted job."""

import importlib
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path


def docker(*args):
    return subprocess.check_output(["docker", *args], text=True, stderr=subprocess.DEVNULL).strip()


def state_path():
    return Path(os.environ["RUNNER_TEMP"]) / f"ai-bdd-mariadb-{os.environ['GATE']}.json"


def start():
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ["GATE"] not in {"G2", "G6"}:
        raise RuntimeError("Only isolated Runner database jobs are supported")
    owner = secrets.token_hex(24)
    name = "ai-bdd-test-" + secrets.token_hex(12)
    image = "mariadb:11.8.6"
    server_id = 7362 if os.environ["GATE"] == "G2" else 7366
    root_password, password = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    for secret in (root_password, password):
        print(f"::add-mask::{secret}", flush=True)
    state_path().write_text(json.dumps({"name": name, "owner": owner}), encoding="utf-8")
    subprocess.run(["docker", "pull", image], check=True)
    environment = dict(os.environ, MARIADB_ROOT_PASSWORD=root_password)
    subprocess.run([
        "docker", "run", "--detach", "--name", name, "--label", f"ai-bdd-owner={owner}",
        "--publish", "127.0.0.1::3306", "--env", "MARIADB_ROOT_PASSWORD",
        "--health-cmd", "healthcheck.sh --connect --innodb_initialized",
        "--health-interval", "2s", "--health-timeout", "5s", "--health-retries", "60",
        image, f"--server-id={server_id}",
    ], check=True, env=environment, stdout=subprocess.DEVNULL)
    port = int(docker("port", name, "3306/tcp").rsplit(":", 1)[1])
    driver = importlib.import_module("pymysql")
    deadline = time.monotonic() + 150
    while True:
        try:
            if docker("inspect", "--format", "{{.State.Health.Status}}", name) != "healthy":
                raise RuntimeError("MariaDB not healthy yet")
            connection = driver.connect(host="127.0.0.1", port=port, user="root",
                                        password=root_password, connect_timeout=3, autocommit=True)
            break
        except (driver.MySQLError, RuntimeError):
            if time.monotonic() >= deadline:
                raise RuntimeError("Isolated MariaDB readiness timed out") from None
            time.sleep(1)
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION(), @@server_id")
            version, actual_id = cursor.fetchone()
            if not str(version).startswith("11.8.6-MariaDB") or int(actual_id) != server_id:
                raise RuntimeError("Unexpected test database version/identity")
            cursor.execute("CREATE USER 'ci_test'@'%%' IDENTIFIED BY %s", (password,))
            # Grants cover only test-prefixed databases; no global or production privileges.
            cursor.execute(r"GRANT ALL PRIVILEGES ON `bdd\_test\_%`.* TO 'ci_test'@'%'")
    values = {"HOST": "127.0.0.1", "PORT": port, "USER": "ci_test", "PASSWORD": password,
              "SERVER_ID": server_id, "DISPOSABLE": "YES"}
    with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"AI_BDD_TEST_DB_{key}={value}\n")
    report = Path("reports")
    report.mkdir(exist_ok=True)
    (report / "mariadb.json").write_text(json.dumps({
        "image": image, "version": version, "server_id": server_id,
        "image_digests": json.loads(docker("image", "inspect", image, "--format", "{{json .RepoDigests}}")),
        "host": "127.0.0.1", "port": port, "ownership": "random per-job container label",
    }, indent=2), encoding="utf-8")
    print(f"Disposable MariaDB {version} ready; test-only grants, loopback binding")


def stop():
    if not state_path().exists():
        print("No database container was requested")
        return
    state = json.loads(state_path().read_text(encoding="utf-8"))
    try:
        details = json.loads(docker("inspect", state["name"]))[0]
    except subprocess.CalledProcessError:
        print("Database container is absent")
        return
    if details["Config"]["Labels"].get("ai-bdd-owner") != state["owner"]:
        raise RuntimeError("Refusing container cleanup: ownership mismatch")
    docker("rm", "--force", "--volumes", state["name"])
    print("Owned disposable MariaDB container removed")


if __name__ == "__main__":
    try:
        {"start": start, "stop": stop}[sys.argv[1]]()
    except Exception as exc:
        # Driver exceptions may include credentials or data; expose only type/numeric code.
        code = exc.args[0] if exc.args and isinstance(exc.args[0], int) else "see step context"
        print(f"Runner database operation failed: {type(exc).__name__}, code={code}", file=sys.stderr)
        raise SystemExit(1) from None
