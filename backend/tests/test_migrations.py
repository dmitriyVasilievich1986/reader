"""Tests for Alembic migrations, driven through the actual ``alembic`` command API.

These tests exercise the real migration pipeline (``env.py`` + revision files)
against a per-test SQLite database, so any breakage in revision scripts or in
the async runner inside ``env.py`` is caught here.

``APPLICATION_TABLES`` lists ORM tables expected after ``upgrade head``; helpers
introspect SQLite with :mod:`sqlite3` for deterministic assertions.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import ALEMBIC_INI

APPLICATION_TABLES: frozenset[str] = frozenset(
    {"author", "book", "category", "category_book_table", "page"},
)


def _table_names(db_path: Path) -> set[str]:
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
        test_config_file (pathlib.Path): Minimal config YAML path from ``conftest``.

    Returns:
        Config: Parsed Alembic configuration pointing at ``ALEMBIC_INI``.

    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    return Config(str(ALEMBIC_INI))


class TestUpgrade:
    """``alembic upgrade head`` against a fresh database."""

    def test_creates_sqlite_file(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Create the SQLite database file when upgrading against a new path.

        Args:
            alembic_config (Config): Alembic config for upgrade.
            sqlite_db_path (pathlib.Path): Expected database file location.

        Returns:
            None

        """
        assert not sqlite_db_path.exists()
        command.upgrade(alembic_config, "head")
        assert sqlite_db_path.exists()

    def test_creates_all_application_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Materialise every application table declared in ``APPLICATION_TABLES``.

        Args:
            alembic_config (Config): Alembic config for upgrade.
            sqlite_db_path (pathlib.Path): SQLite file to introspect post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")

        tables = _table_names(sqlite_db_path)
        missing = APPLICATION_TABLES - tables
        assert not missing, f"Missing tables after upgrade: {missing}"

    def test_records_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Persist the head revision in ``alembic_version``.

        Args:
            alembic_config (Config): Alembic config for upgrade.
            sqlite_db_path (pathlib.Path): SQLite file to read ``version_num``.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")

        assert "alembic_version" in _table_names(sqlite_db_path)

        conn = sqlite3.connect(str(sqlite_db_path))
        try:
            versions = [row[0] for row in conn.execute("SELECT version_num FROM alembic_version")]
        finally:
            conn.close()

        assert versions == ["8e3f5d72efaf"]

    def test_book_has_author_foreign_key(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare ``book.author_id`` as a foreign key to ``author.id``.

        Args:
            alembic_config (Config): Alembic config for upgrade.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")

        conn = sqlite3.connect(str(sqlite_db_path))
        try:
            fks = conn.execute("PRAGMA foreign_key_list('book')").fetchall()
        finally:
            conn.close()

        referenced = {(row[2], row[3], row[4]) for row in fks}
        assert ("author", "author_id", "id") in referenced


class TestDowngrade:
    """``alembic downgrade base`` after upgrading should drop application tables."""

    def test_downgrade_removes_application_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Remove application tables when downgrading to base.

        Args:
            alembic_config (Config): Alembic config for upgrade then downgrade.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")
        command.downgrade(alembic_config, "base")

        remaining = _table_names(sqlite_db_path)
        leaked = APPLICATION_TABLES & remaining
        assert not leaked, f"Tables not dropped on downgrade: {leaked}"


class TestRoundTrip:
    """Repeated upgrade/downgrade cycles leave the schema in a consistent state."""

    def test_upgrade_downgrade_upgrade_restores_schema(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Restore full schema after downgrade then upgrade again.

        Args:
            alembic_config (Config): Alembic config across the cycle.
            sqlite_db_path (pathlib.Path): SQLite file after final upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")
        command.downgrade(alembic_config, "base")
        command.upgrade(alembic_config, "head")

        tables = _table_names(sqlite_db_path)
        assert APPLICATION_TABLES.issubset(tables)
