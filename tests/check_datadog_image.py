"""Run only against disposable Docker fixtures, never against the HomeLab."""

import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import uuid

# This negative control must retain the release with the observed PG18 defect.
BASELINE_IMAGE = "gcr.io/datadoghq/agent:7.73.0-jmx@sha256:1da9f3cf352b1e1578dc7ba3c1be55a6b7581320ed4f8d7f973632d88c7dcf6e"
POSTGRES_IMAGE = "postgres:18.3"


def docker(*arguments: str, timeout: int = 180, environment: dict | None = None) -> str:
    result = subprocess.run(["docker", *arguments], capture_output=True, text=True,
                            timeout=timeout, env=environment)
    if result.returncode:
        # Do not include captured configuration, check output, or fixture passwords.
        text = (result.stdout + result.stderr).lower()
        categories = [word for word in ("auth_token", "ipc_cert", "certificate", "hostname", "no valid check",
                      "permission denied", "read-only", "connection refused", "no such file", "configuration",
                      "could not load", "api key", "unknown flag") if word in text]
        raise RuntimeError(f"Docker {arguments[0]} failed (exit {result.returncode}, categories={categories})")
    return result.stdout


def parse_check_output(output: str) -> list:
    decoder = json.JSONDecoder()
    for line in output.splitlines(keepends=True):
        if not line.startswith("["):
            continue
        offset = output.index(line)
        try:
            value, _ = decoder.raw_decode(output[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and value and all(
                isinstance(row, dict) and "runner" in row and "aggregator" in row for row in value):
            return value
    raise ValueError("Agent did not return check-runner JSON")


def assert_candidate_output(output: str) -> None:
    instances = parse_check_output(output)
    if any(row["runner"].get("TotalErrors", 1) != 0 or
           row["runner"].get("TotalRuns", 0) < 2 for row in instances):
        raise ValueError("Candidate PostgreSQL check reported errors or insufficient runs")
    metrics = {sample["metric"] for row in instances
               for sample in row["aggregator"].get("metrics", [])}
    required = {"postgresql.wal.records", "postgresql.wal.bytes"}
    if not required.issubset(metrics):
        raise ValueError("Candidate did not emit the PostgreSQL WAL metrics")


def write_fixture_configuration(directory: Path, password: str) -> None:
    # This invalid placeholder is not a credential. `agent check` uses noop forwarders.
    agent_config = "hostname: ci-pg18-fixture\nlog_level: error\napi_key: '00000000000000000000000000000000'\n"
    # JSON strings are also valid YAML scalars. The random password is file-only.
    postgres_config = ("init_config: {}\ninstances:\n  - host: postgres\n"
                       "    port: 5432\n    username: postgres\n    dbname: postgres\n"
                       f"    password: {json.dumps(password)}\n    dbm: false\n"
                       "    database_autodiscovery:\n      enabled: true\n")
    # The one-shot CLI requires an IPC token even without a running Agent daemon.
    files = [("datadog.yaml", agent_config), ("postgres.yaml", postgres_config),
             ("auth_token", secrets.token_hex(32))]
    for name, content in files:
        path = directory / name
        path.write_text(content)
        path.chmod(0o600)


def start_postgres(name: str, network: str, password: str) -> None:
    docker("run", "--detach", "--name", name, "--network", network,
           "--network-alias", "postgres", "--env", "POSTGRES_PASSWORD", POSTGRES_IMAGE,
           environment={**os.environ, "POSTGRES_PASSWORD": password})
    wait = "for i in $(seq 1 30); do pg_isready -h 127.0.0.1 -U postgres >/dev/null && exit 0; sleep 1; done; exit 1"
    docker("exec", name, "sh", "-c", wait, timeout=40)
    docker("exec", name, "psql", "-U", "postgres", "-v", "ON_ERROR_STOP=1", "-c",
           "CREATE TABLE telemetry_fixture (value integer); INSERT INTO telemetry_fixture VALUES (1);")


def check_postgres(image: str, name: str, network: str, directory: Path) -> str:
    return docker("run", "--rm", "--name", name, "--user", "0", "--network", network,
                  "--mount", f"type=bind,src={directory / 'datadog.yaml'},dst=/etc/datadog-agent/datadog.yaml,readonly",
                  "--mount", f"type=bind,src={directory / 'postgres.yaml'},dst=/etc/datadog-agent/conf.d/postgres.d/conf.yaml,readonly",
                  "--mount", f"type=bind,src={directory / 'auth_token'},dst=/etc/datadog-agent/auth_token,readonly",
                  "--entrypoint", "agent", image, "check", "postgres", "--json", "--check-rate")


def assert_installed_integrations(image: str, name: str) -> None:
    imports = ("import importlib, importlib.metadata as m; "
               "expected={'datadog-emqx':'1.1.0','datadog-grafana':'1.0.0',"
               "'datadog-nextcloud':'2.0.0','datadog-postgres':'23.3.3'}; "
               "[importlib.import_module('datadog_checks.'+p.removeprefix('datadog-')) for p in expected]; "
               "assert all(m.version(p)==v for p,v in expected.items())")
    docker("run", "--rm", "--name", name, "--network", "none", "--entrypoint",
           "/opt/datadog-agent/embedded/bin/python", image, "-c", imports)
    docker("run", "--rm", "--name", name, "--network", "none", "--entrypoint",
           "java", image, "-version")


def assert_old_query_fails(image: str, name: str, network: str, directory: Path, database: str) -> int:
    check_postgres(image, name, network, directory)
    result = subprocess.run(["docker", "logs", database], capture_output=True, text=True, timeout=15)
    logs = result.stdout + result.stderr
    if result.returncode or 'column "wal_write" does not exist' not in logs:
        raise ValueError("Negative control did not reproduce the observed PostgreSQL 18 failure")
    return logs.count("ERROR:")


def assert_no_new_sql_errors(database: str, baseline_errors: int) -> None:
    result = subprocess.run(["docker", "logs", database], capture_output=True, text=True, timeout=15)
    if result.returncode or (result.stdout + result.stderr).count("ERROR:") != baseline_errors:
        raise ValueError("Candidate generated new PostgreSQL SQL errors")


def cleanup_fixtures(names: list, network: str) -> None:
    subprocess.run(["docker", "rm", "--force", *names], capture_output=True, timeout=30)
    subprocess.run(["docker", "network", "rm", network], capture_output=True, timeout=30)


def verify_image(image: str) -> None:
    suffix = uuid.uuid4().hex[:12]
    network, database, agent = [f"dd-{kind}-{suffix}" for kind in ["network", "database", "agent"]]
    try:
        docker("network", "create", "--internal", network)
        assert_installed_integrations(image, agent)
        with tempfile.TemporaryDirectory(prefix="dd-pg18-") as temporary:
            directory, password = Path(temporary), secrets.token_hex(24)
            write_fixture_configuration(directory, password)
            start_postgres(database, network, password)
            print("Fixture ready. Run the fixed Agent 7.73 negative control.", flush=True)
            baseline_errors = assert_old_query_fails(BASELINE_IMAGE, agent, network, directory, database)
            print("Negative control reproduced wal_write. Run the candidate check.", flush=True)
            assert_candidate_output(check_postgres(image, agent, network, directory))
            assert_no_new_sql_errors(database, baseline_errors)
        print("PASS: integration imports and pins; PG18 negative control; candidate WAL metrics and SQL checks")
    finally:
        cleanup_fixtures([database, agent], network)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 tests/check_datadog_image.py IMAGE")
    try:
        verify_image(sys.argv[1])
    except (RuntimeError, ValueError, subprocess.TimeoutExpired, OSError) as error:
        print(f"FAIL: {type(error).__name__}: {error if isinstance(error, (RuntimeError, ValueError)) else 'fixture execution failed'}", file=sys.stderr)
        raise SystemExit(1)
