"""Shared fixtures and helpers for per-revision Alembic migration tests.

Provides ``alembic_config`` bound to this repo's ``alembic.ini`` and a small
SQLite introspection helper (:func:`table_names`) used across the migration
test modules.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic.config import Config

from ..conftest import ALEMBIC_INI


def table_names(db_path: Path) -> set[str]:
    """List user tables in an on-disk SQLite file.

    Ignores SQLite internal schemas (names prefixed ``sqlite_``).

    Args:
        db_path (pathlib.Path): Database file path. If the file does not exist,
            returns an empty set.

    Returns:
        set[str]: Table names present in ``sqlite_master``.

    """
    if not db_path.exists():
        return set()
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
        ).fetchall()
    finally:
        conn.close()
    return {row[0] for row in rows}


def alembic_version(db_path: Path) -> list[str]:
    """Read ``alembic_version.version_num`` from a migrated SQLite database.

    Args:
        db_path (pathlib.Path): SQLite file containing the ``alembic_version``
            table.

    Returns:
        list[str]: Recorded revision identifiers (typically one entry).

    """
    conn = sqlite3.connect(str(db_path))
    try:
        return [row[0] for row in conn.execute("SELECT version_num FROM alembic_version")]
    finally:
        conn.close()


@pytest.fixture
def alembic_config(
    monkeypatch: pytest.MonkeyPatch,
    test_config_file: Path,
) -> Config:
    """Provide an Alembic ``Config`` bound to this repo's ``alembic.ini``.

    Ensures migrations resolve ``CONFIG_FILE_PATH`` to the same per-test YAML
    as ``AppConfig`` fixtures (database URL aligns with ``sqlite_db_path``).

    Args:
        monkeypatch (pytest.MonkeyPatch): Sets ``CONFIG_FILE_PATH`` for the test.
        test_config_file (pathlib.Path): Minimal config YAML path from
            ``tests.conftest``.

    Returns:
        Config: Parsed Alembic configuration pointing at ``ALEMBIC_INI``.

    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    return Config(str(ALEMBIC_INI))
