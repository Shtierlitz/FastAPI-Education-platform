import importlib.util
import subprocess
from pathlib import Path

import envparse
import yaml


def test_settings_import_without_dotenv_only_requires_runtime_database_url(
    monkeypatch,
):
    monkeypatch.chdir(Path.cwd() / "tests")
    monkeypatch.setenv(
        "REAL_DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/app"
    )
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)
    monkeypatch.setenv("SECRET_KEY", "runtime-secret")
    monkeypatch.setattr(envparse.Env, "read_envfile", lambda self, envfile: None)
    spec = importlib.util.spec_from_file_location(
        "_settings_without_dotenv",
        Path.cwd().parent / "settings.py",
    )
    settings_without_dotenv = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(settings_without_dotenv)

    assert (
        settings_without_dotenv.TEST_DATABASE_URL
        == settings_without_dotenv.REAL_DATABASE_URL
    )
    assert settings_without_dotenv.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings_without_dotenv.SECRET_KEY == "runtime-secret"


def test_settings_requires_secret_key_without_dotenv(monkeypatch):
    monkeypatch.chdir(Path.cwd() / "tests")
    monkeypatch.setenv(
        "REAL_DATABASE_URL", "postgresql+asyncpg://user:pass@db:5432/app"
    )
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setattr(envparse.Env, "read_envfile", lambda self, envfile: None)
    spec = importlib.util.spec_from_file_location(
        "_settings_without_secret",
        Path.cwd().parent / "settings.py",
    )
    settings_without_secret = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(settings_without_secret)
    except envparse.ConfigurationError as err:
        assert "SECRET_KEY" in str(err)
    else:
        raise AssertionError("settings import should require SECRET_KEY")


def test_production_code_does_not_log_sensitive_auth_or_sql_data():
    assert "echo=True" not in Path("db/session.py").read_text()
    assert "print(" not in Path("api/actions/auth.py").read_text()


def test_ci_compose_uses_async_database_url_for_app():
    compose = yaml.safe_load(Path("docker-compose-ci.yaml").read_text())
    db_environment = compose["services"]["db"]["environment"]
    app_environment = compose["services"]["FastApi_education_platform_app"][
        "environment"
    ]

    assert app_environment["REAL_DATABASE_URL"].startswith("postgresql+asyncpg://")
    assert "${POSTGRES_USER:-" in app_environment["REAL_DATABASE_URL"]
    assert "${POSTGRES_PASSWORD:-" in app_environment["REAL_DATABASE_URL"]
    assert "${POSTGRES_DB:-" in app_environment["REAL_DATABASE_URL"]
    assert app_environment["ACCESS_TOKEN_EXPIRE_MINUTES"] == (
        "${ACCESS_TOKEN_EXPIRE_MINUTES:-30}"
    )
    assert app_environment["SECRET_KEY"] == "${SECRET_KEY:-demo-secret-change-me}"
    assert "POSTGRES_USER=${POSTGRES_USER:-app_user}" in db_environment
    assert "POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-change_me}" in db_environment
    assert "POSTGRES_DB=${POSTGRES_DB:-app_db}" in db_environment


def test_dockerignore_excludes_local_secrets_and_build_artifacts():
    dockerignore = Path(".dockerignore").read_text().splitlines()

    assert ".env" in dockerignore
    assert ".venv/" in dockerignore
    assert "__pycache__/" in dockerignore
    assert ".git/" in dockerignore


def test_make_up_and_down_do_not_prefix_docker_twice():
    up_result = subprocess.run(
        ["make", "-n", "up"],
        capture_output=True,
        text=True,
    )
    down_result = subprocess.run(
        ["make", "-n", "down"],
        capture_output=True,
        text=True,
    )

    assert up_result.returncode == 0, up_result.stderr
    assert down_result.returncode == 0, down_result.stderr
    assert "docker docker" not in up_result.stdout
    assert "docker docker" not in down_result.stdout
    assert "docker compose -f docker-compose-local.yaml up -d" in up_result.stdout
    assert "docker compose -f docker-compose-local.yaml down" in down_result.stdout


def test_dockerfile_runs_migrations_before_starting_app():
    dockerfile = Path("Dockerfile").read_text()

    assert "alembic upgrade head" in dockerfile
    assert "python main.py" in dockerfile
    assert dockerfile.index("alembic upgrade head") < dockerfile.index("python main.py")


def test_ping_route_registered_at_root_ping():
    import main

    route_paths = {route.path for route in main.app.routes}

    assert "/ping" in route_paths
    assert "/ping/ping" not in route_paths
