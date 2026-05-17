"""Shared pytest fixtures: per-test SQLite database, config, and singleton reset."""

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
    """Clear all Singleton instances so each test gets fresh AppConfig and DB client."""
    Singleton._instances.clear()  # noqa: SLF001
    yield
    Singleton._instances.clear()  # noqa: SLF001


@pytest.fixture
def sqlite_db_path(tmp_path: Path) -> Path:
    """Path to a per-test SQLite file (not yet created)."""
    return tmp_path / "test.sqlite3"


@pytest.fixture
def test_config_file(tmp_path: Path, sqlite_db_path: Path) -> Path:
    """Write a minimal AppConfig YAML pointing at the per-test SQLite file."""
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
                "origins": "*",
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
        },
    }
    config_path = tmp_path / "test.yaml"
    config_path.write_text(yaml.safe_dump(payload))
    return config_path


@pytest.fixture
def app_config(monkeypatch: pytest.MonkeyPatch, test_config_file: Path) -> AppConfig:
    """Build a fresh AppConfig that reads from the test YAML."""
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    return AppConfig.get_or_create(reload=True)


@pytest.fixture
def db_client(app_config: AppConfig) -> AsyncDatabaseClient:
    """Construct AsyncDatabaseClient bound to the per-test SQLite file."""
    return AsyncDatabaseClient(app_config=app_config)
