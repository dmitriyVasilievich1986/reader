"""Tests for Alembic revision ``b922d12d33b3`` — add ``book.watches_count``.

Exercises the fourth migration in isolation: upgrading from the prior revision
(``ca414c66f0fa``) to this one should add a NOT NULL ``watches_count`` column
of integer type to ``book``; downgrading should drop only that column and
leave every other ``book`` column intact.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import alembic_version, table_names

REVISION = "b922d12d33b3"
PREVIOUS_REVISION = "ca414c66f0fa"

NEW_COLUMN = "watches_count"
PRE_EXISTING_TABLES: frozenset[str] = frozenset(
    {"author", "book", "category", "category_book_table", "page", "user"},
)
PRE_EXISTING_BOOK_COLUMNS: frozenset[str] = frozenset(
    {
        "id",
        "name",
        "description",
        "cover",
        "author_id",
        "created_at",
        "updated_at",
    },
)


def _book_table_info(db_path: Path) -> list[tuple]:
    """Return raw ``PRAGMA table_info('book')`` rows.

    Args:
        db_path (pathlib.Path): SQLite file to inspect.

    Returns:
        list[tuple]: One row per column ``(cid, name, type, notnull, dflt, pk)``.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        return conn.execute("PRAGMA table_info('book')").fetchall()
    finally:
        conn.close()


@pytest.mark.migrations
class TestUpgradeToAddWatchesCountRevision:
    """``alembic upgrade b922d12d33b3`` adds ``watches_count`` to ``book``."""

    def test_records_revision_in_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Persist ``b922d12d33b3`` in ``alembic_version`` once applied.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert alembic_version(sqlite_db_path) == [REVISION]

    def test_book_has_watches_count_column(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Add ``watches_count`` to ``book``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        columns = {row[1] for row in _book_table_info(sqlite_db_path)}
        assert NEW_COLUMN in columns

    def test_watches_count_is_not_null_integer(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare ``watches_count`` as ``NOT NULL INTEGER``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        row = next(
            (r for r in _book_table_info(sqlite_db_path) if r[1] == NEW_COLUMN),
            None,
        )
        assert row is not None, f"{NEW_COLUMN} column missing from book"
        assert row[2].upper() == "INTEGER", f"{NEW_COLUMN} type expected INTEGER, got {row[2]}"
        assert bool(row[3]) is True, f"{NEW_COLUMN} should be NOT NULL"

    def test_preserves_pre_existing_book_columns(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Leave the rest of ``book``'s column set untouched.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        columns = {row[1] for row in _book_table_info(sqlite_db_path)}
        missing = PRE_EXISTING_BOOK_COLUMNS - columns
        assert not missing, f"Missing pre-existing columns on book: {missing}"

    def test_preserves_pre_existing_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Leave the prior-revision table set in place.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert PRE_EXISTING_TABLES.issubset(table_names(sqlite_db_path))


@pytest.mark.migrations
class TestDowngradeFromAddWatchesCountRevision:
    """Downgrading from ``b922d12d33b3`` only removes ``book.watches_count``."""

    def test_downgrade_removes_watches_count_column(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Drop ``watches_count`` when stepping back one revision.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        columns = {row[1] for row in _book_table_info(sqlite_db_path)}
        assert NEW_COLUMN not in columns

    def test_downgrade_preserves_pre_existing_book_columns(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Leave the other ``book`` columns intact after downgrade.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        columns = {row[1] for row in _book_table_info(sqlite_db_path)}
        missing = PRE_EXISTING_BOOK_COLUMNS - columns
        assert not missing, f"Pre-existing columns lost on downgrade: {missing}"

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
