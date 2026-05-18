"""Shared pytest fixtures for the Reader backend integration tests.

``reset_singletons`` clears :class:`~reader.utils.singleton.Singleton` between
tests. Other fixtures provision a disposable SQLite database path, a matching
minimal YAML config file, ``AppConfig``, and ``AsyncDatabaseClient`` instances.

Module-level constants ``BACKEND_ROOT`` and ``ALEMBIC_INI`` point at backend
sources for migration-related tests elsewhere in the suite.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml

from reader.config import AppConfig
from reader.services.database import AsyncDatabaseClient
from reader.utils.singleton import Singleton

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_ROOT / "src" / "reader" / "services" / "alembic" / "alembic.ini"


@pytest.fixture(autouse=True)
def reset_singletons() -> Iterator[None]:
    """Clear Singleton registries around each test for isolated state.

    Yields:
        None: Suspends execution so pytest runs the test, then clears
            registries again in teardown.

    Note:
        Accesses ``Singleton._instances`` directly to reset global state used
        by ``AppConfig.get_or_create`` and related clients.

    """
    Singleton._instances.clear()  # noqa: SLF001
    yield
    Singleton._instances.clear()  # noqa: SLF001


@pytest.fixture
def sqlite_db_path(tmp_path: Path) -> Path:
    """Return a deterministic SQLite file path for the current test.

    Args:
        tmp_path (pathlib.Path): Pytest-provided temporary directory unique to
            the test.

    Returns:
        pathlib.Path: Path to the SQLite database file; the file is not created
            by this fixture.

    """
    return tmp_path / "test.sqlite3"


@pytest.fixture
def test_config_file(tmp_path: Path, sqlite_db_path: Path) -> Path:
    """Write minimal ``AppConfig`` YAML that targets the per-test SQLite file.

    Args:
        tmp_path (pathlib.Path): Pytest-provided temporary directory unique to
            the test.
        sqlite_db_path (pathlib.Path): Database path injected into the YAML
            ``services.database.host`` field.

    Returns:
        pathlib.Path: Absolute path to the written ``test.yaml`` file.

    """
    payload = {
        "info": {
            "name": "Reader",
            "description": "test",
            "api_info": {
                "app_port": 8000,
                "debug": False,
                "log_level": "INFO",
            },
            "cors_info": {
                "origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["GET"],
                "allow_headers": ["*"],
            },
        },
        "services": {
            "database": {
                "provider": "sqlite+aiosqlite",
                "host": str(sqlite_db_path),
            },
            "auth": {
                "jwt_secret_key": "test-jwt-secret-key",
                "jwt_algorithm": "HS256",
            },
        },
    }
    config_path = tmp_path / "test.yaml"
    config_path.write_text(yaml.safe_dump(payload))
    return config_path


@pytest.fixture
def app_config(monkeypatch: pytest.MonkeyPatch, test_config_file: Path) -> AppConfig:
    """Load ``AppConfig`` from the test YAML via ``CONFIG_FILE_PATH``.

    Args:
        monkeypatch (pytest.MonkeyPatch): Sets ``CONFIG_FILE_PATH`` for the
            duration of the test.
        test_config_file (pathlib.Path): Path to YAML written by
            ``test_config_file``.

    Returns:
        AppConfig: Reloaded singleton instance backed by ``test_config_file``.

    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    return AppConfig.get_or_create(reload=True)


@pytest.fixture
def db_client(app_config: AppConfig) -> AsyncDatabaseClient:
    """Expose an ``AsyncDatabaseClient`` bound to the per-test configuration.

    Args:
        app_config (AppConfig): Configuration whose database section points at
            the test SQLite database.

    Returns:
        AsyncDatabaseClient: Async client constructed from ``app_config``.

    """
    return AsyncDatabaseClient(app_config=app_config)
