"""Tests for Alembic revision ``ca414c66f0fa`` — add ``created_at``/``updated_at``.

Exercises the third migration in isolation: upgrading from the prior revision
(``14ba01e0e048``) to this one should add ``created_at`` and ``updated_at``
columns (NOT NULL, ``DateTime``) to each of ``author``, ``book``, ``category``,
``page``, and ``user``; downgrading should drop them while leaving every other
column on those tables intact.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import alembic_version, table_names

REVISION = "ca414c66f0fa"
PREVIOUS_REVISION = "14ba01e0e048"

TIMESTAMPED_TABLES: frozenset[str] = frozenset(
    {"author", "book", "category", "page", "user"},
)
NEW_COLUMNS: frozenset[str] = frozenset({"created_at", "updated_at"})
PRE_EXISTING_TABLES: frozenset[str] = frozenset(
    {"author", "book", "category", "category_book_table", "page", "user"},
)


def _columns(db_path: Path, table: str) -> dict[str, tuple]:
    """Return ``PRAGMA table_info`` rows keyed by column name.

    Args:
        db_path (pathlib.Path): SQLite file to inspect.
        table (str): Table to introspect.

    Returns:
        dict[str, tuple]: ``column_name -> (cid, name, type, notnull, dflt, pk)``.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(f"PRAGMA table_info('{table}')").fetchall()
    finally:
        conn.close()
    return {row[1]: row for row in rows}


@pytest.mark.migrations
class TestUpgradeToAddCreatedUpdatedColumnsRevision:
    """``alembic upgrade ca414c66f0fa`` adds timestamp columns to core tables."""

    def test_records_revision_in_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Persist ``ca414c66f0fa`` in ``alembic_version`` once applied.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert alembic_version(sqlite_db_path) == [REVISION]

    @pytest.mark.parametrize("table", sorted(TIMESTAMPED_TABLES))
    def test_table_has_new_timestamp_columns(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
        table: str,
    ) -> None:
        """Add ``created_at`` and ``updated_at`` to every timestamped table.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.
            table (str): Target table receiving the timestamp columns.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        columns = set(_columns(sqlite_db_path, table))
        missing = NEW_COLUMNS - columns
        assert not missing, f"Missing timestamp columns on {table}: {missing}"

    @pytest.mark.parametrize("table", sorted(TIMESTAMPED_TABLES))
    def test_timestamp_columns_are_not_null_datetime(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
        table: str,
    ) -> None:
        """Declare both new columns as ``NOT NULL DATETIME``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.
            table (str): Target table receiving the timestamp columns.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        info = _columns(sqlite_db_path, table)
        for column in NEW_COLUMNS:
            row = info[column]
            assert row[2].upper() == "DATETIME", (
                f"{table}.{column} type expected DATETIME, got {row[2]}"
            )
            assert bool(row[3]) is True, f"{table}.{column} should be NOT NULL"

    def test_preserves_pre_existing_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Leave the prior-revision table set untouched.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert PRE_EXISTING_TABLES.issubset(table_names(sqlite_db_path))


@pytest.mark.migrations
class TestDowngradeFromAddCreatedUpdatedColumnsRevision:
    """Downgrading from ``ca414c66f0fa`` drops only the new timestamp columns."""

    @pytest.mark.parametrize("table", sorted(TIMESTAMPED_TABLES))
    def test_downgrade_removes_timestamp_columns(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
        table: str,
    ) -> None:
        """Drop ``created_at`` and ``updated_at`` when stepping back one revision.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.
            table (str): Target table whose timestamp columns should be gone.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        columns = set(_columns(sqlite_db_path, table))
        leaked = NEW_COLUMNS & columns
        assert not leaked, f"Timestamp columns lingered on {table}: {leaked}"

    def test_downgrade_preserves_pre_existing_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Leave every prior-revision table in place after downgrade.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        assert PRE_EXISTING_TABLES.issubset(table_names(sqlite_db_path))

    def test_downgrade_resets_alembic_version_to_previous(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Update ``alembic_version`` to the predecessor revision.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        assert alembic_version(sqlite_db_path) == [PREVIOUS_REVISION]
