"""Tests for Alembic migrations, driven through the actual ``alembic`` command API.

These tests exercise the real migration pipeline (``env.py`` + revision files)
against a per-test SQLite database, so any breakage in revision scripts or in
the async runner inside ``env.py`` is caught here.
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
    """Return the set of non-internal table names in the SQLite database file."""
    if not db_path.exists():
        return set()
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%'",
        ).fetchall()
    finally:
        conn.close()
    return {row[0] for row in rows}


@pytest.fixture
def alembic_config(
    monkeypatch: pytest.MonkeyPatch,
    test_config_file: Path,
) -> Config:
    """Build an Alembic ``Config`` that will read the per-test AppConfig YAML."""
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    return Config(str(ALEMBIC_INI))


class TestUpgrade:
    """``alembic upgrade head`` against a fresh database."""

    def test_creates_sqlite_file(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Running migrations on a fresh path creates the SQLite database file."""
        assert not sqlite_db_path.exists()
        command.upgrade(alembic_config, "head")
        assert sqlite_db_path.exists()

    def test_creates_all_application_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """All declared application tables exist after upgrading to head."""
        command.upgrade(alembic_config, "head")

        tables = _table_names(sqlite_db_path)
        missing = APPLICATION_TABLES - tables
        assert not missing, f"Missing tables after upgrade: {missing}"

    def test_records_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Alembic stamps the database with the head revision identifier."""
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
        """The book table is created with a foreign key to author.id."""
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
        """All application tables are gone after downgrading to base."""
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
        """After down/up the application tables are back."""
        command.upgrade(alembic_config, "head")
        command.downgrade(alembic_config, "base")
        command.upgrade(alembic_config, "head")

        tables = _table_names(sqlite_db_path)
        assert APPLICATION_TABLES.issubset(tables)
