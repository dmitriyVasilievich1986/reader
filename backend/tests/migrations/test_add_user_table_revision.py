"""Tests for Alembic revision ``14ba01e0e048`` — add ``user`` table.

Exercises the second migration in isolation: upgrading from the prior revision
(``8e3f5d72efaf``) to this one should add the ``user`` table with its full
column set and unique constraints; downgrading should remove only ``user`` and
leave the earlier-revision tables intact.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import alembic_version, table_names

REVISION = "14ba01e0e048"
PREVIOUS_REVISION = "8e3f5d72efaf"

USER_COLUMNS: frozenset[str] = frozenset(
    {"id", "username", "email", "password", "first_name", "last_name", "photo_url", "is_admin", "is_active"},
)
NULLABLE_COLUMNS: frozenset[str] = frozenset({"first_name", "last_name", "photo_url"})
NOT_NULL_COLUMNS: frozenset[str] = frozenset(
    {"username", "email", "password", "is_admin", "is_active"},
)
PRE_EXISTING_TABLES: frozenset[str] = frozenset(
    {"author", "book", "category", "category_book_table", "page"},
)


def _user_table_info(db_path: Path) -> list[tuple]:
    """Return raw ``PRAGMA table_info('user')`` rows.

    Args:
        db_path (pathlib.Path): SQLite file to inspect.

    Returns:
        list[tuple]: One row per column ``(cid, name, type, notnull, dflt, pk)``.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute("PRAGMA table_info('user')").fetchall()
    finally:
        conn.close()


def _unique_columns(db_path: Path, table: str) -> set[str]:
    """Return single-column ``UNIQUE`` constraints declared on ``table``.

    Args:
        db_path (pathlib.Path): SQLite file to inspect.
        table (str): Target table name.

    Returns:
        set[str]: Column names that participate in a unique index alone.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        indexes = conn.execute(f"PRAGMA index_list('{table}')").fetchall()
        uniques: set[str] = set()
        for index in indexes:
            _seq, name, unique, _origin, _partial = index
            if not unique:
                continue
            cols = conn.execute(f"PRAGMA index_info('{name}')").fetchall()
            if len(cols) == 1:
                uniques.add(cols[0][2])
        return uniques
    finally:
        conn.close()


@pytest.mark.migrations
class TestUpgradeToAddUserTableRevision:
    """``alembic upgrade 14ba01e0e048`` introduces a populated ``user`` table."""

    def test_creates_user_table(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Add ``user`` on top of the previous-revision schema.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert "user" in table_names(sqlite_db_path)

    def test_records_revision_in_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Persist ``14ba01e0e048`` in ``alembic_version`` once applied.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert alembic_version(sqlite_db_path) == [REVISION]

    def test_user_table_has_all_expected_columns(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare the full column set the ``User`` ORM model expects.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        columns = {row[1] for row in _user_table_info(sqlite_db_path)}
        missing = USER_COLUMNS - columns
        assert not missing, f"Missing columns on user: {missing}"

    def test_user_table_nullability_matches_model(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Profile fields stay nullable; credentials and flags are NOT NULL.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        notnull_by_column = {row[1]: bool(row[3]) for row in _user_table_info(sqlite_db_path)}
        for column in NULLABLE_COLUMNS:
            assert notnull_by_column[column] is False, f"{column} should be nullable"
        for column in NOT_NULL_COLUMNS:
            assert notnull_by_column[column] is True, f"{column} should be NOT NULL"

    def test_user_table_primary_key_on_id(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare ``id`` as the single-column primary key.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        pk_columns = [row[1] for row in _user_table_info(sqlite_db_path) if row[5]]
        assert pk_columns == ["id"]

    def test_user_table_unique_constraints(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Enforce per-column uniqueness on ``username`` and ``email``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        uniques = _unique_columns(sqlite_db_path, "user")
        assert {"username", "email"}.issubset(uniques)


@pytest.mark.migrations
class TestDowngradeFromAddUserTableRevision:
    """Downgrading from ``14ba01e0e048`` only removes the ``user`` table."""

    def test_downgrade_removes_user_table(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Drop ``user`` when stepping back one revision.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        assert "user" not in table_names(sqlite_db_path)

    def test_downgrade_preserves_pre_existing_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Leave the prior-revision schema fully intact after downgrade.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        remaining = table_names(sqlite_db_path)
        assert PRE_EXISTING_TABLES.issubset(remaining)

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
