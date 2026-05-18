"""Tests for Alembic revision ``8e3f5d72efaf`` — initial schema.

Exercises the first migration in isolation by upgrading directly to it from
``base`` (rather than to ``head``). Verifies that the five application tables
declared by the revision are created, the ``book.author_id`` foreign key is
declared, the version is recorded, and downgrading back to ``base`` drops
every table the revision introduced.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import alembic_version, table_names

REVISION = "8e3f5d72efaf"
TABLES_INTRODUCED: frozenset[str] = frozenset(
    {"author", "book", "category", "category_book_table", "page"},
)


@pytest.mark.migrations
class TestUpgradeToInitRevision:
    """``alembic upgrade 8e3f5d72efaf`` creates the initial application tables."""

    def test_creates_all_initial_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Materialise every initial-schema table declared by the revision.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file to introspect post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        tables = table_names(sqlite_db_path)
        missing = TABLES_INTRODUCED - tables
        assert not missing, f"Missing tables after upgrade to {REVISION}: {missing}"

    def test_records_revision_in_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Persist ``8e3f5d72efaf`` in ``alembic_version`` when stopped at this rev.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file to read ``version_num``.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert alembic_version(sqlite_db_path) == [REVISION]

    def test_book_has_author_foreign_key(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare ``book.author_id`` as a foreign key to ``author.id``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        conn = sqlite3.connect(str(sqlite_db_path))
        try:
            fks = conn.execute("PRAGMA foreign_key_list('book')").fetchall()
        finally:
            conn.close()

        referenced = {(row[2], row[3], row[4]) for row in fks}
        assert ("author", "author_id", "id") in referenced

    def test_category_book_table_links_book_and_category(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare both foreign keys on the m2m join table.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        conn = sqlite3.connect(str(sqlite_db_path))
        try:
            fks = conn.execute("PRAGMA foreign_key_list('category_book_table')").fetchall()
        finally:
            conn.close()

        referenced = {(row[2], row[3], row[4]) for row in fks}
        assert ("book", "book_id", "id") in referenced
        assert ("category", "category_id", "id") in referenced


@pytest.mark.migrations
class TestDowngradeFromInitRevision:
    """Downgrading from ``8e3f5d72efaf`` to ``base`` drops the initial tables."""

    def test_downgrade_to_base_removes_initial_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Remove every table the revision introduced.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, "base")

        remaining = table_names(sqlite_db_path)
        leaked = TABLES_INTRODUCED & remaining
        assert not leaked, f"Tables not dropped on downgrade: {leaked}"
