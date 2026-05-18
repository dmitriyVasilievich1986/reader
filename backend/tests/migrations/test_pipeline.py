"""Cross-cutting checks for the Alembic upgrade/downgrade pipeline.

Tests behaviour that does not belong to any single revision: ``env.py``
materialising the SQLite file on first upgrade, and the full
``head → base → head`` round-trip leaving the schema consistent.
"""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import table_names

ALL_APPLICATION_TABLES: frozenset[str] = frozenset(
    {"author", "book", "category", "category_book_table", "page", "user"},
)


@pytest.mark.migrations
class TestPipeline:
    """``alembic`` pipeline behaviour orthogonal to any specific revision."""

    def test_upgrade_creates_sqlite_file(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """``env.py`` materialises the SQLite file on first upgrade.

        Args:
            alembic_config (Config): Alembic config for the upgrade run.
            sqlite_db_path (pathlib.Path): Expected database file location.

        Returns:
            None

        """
        assert not sqlite_db_path.exists()
        command.upgrade(alembic_config, "head")
        assert sqlite_db_path.exists()

    def test_head_contains_all_application_tables(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """``head`` aggregates every revision's tables into the live schema.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")

        missing = ALL_APPLICATION_TABLES - table_names(sqlite_db_path)
        assert not missing, f"Missing tables at head: {missing}"

    def test_upgrade_downgrade_upgrade_restores_schema(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Restore the full schema after a downgrade-to-base / upgrade-to-head cycle.

        Args:
            alembic_config (Config): Alembic config across the cycle.
            sqlite_db_path (pathlib.Path): SQLite file after final upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, "head")
        command.downgrade(alembic_config, "base")
        command.upgrade(alembic_config, "head")

        assert ALL_APPLICATION_TABLES.issubset(table_names(sqlite_db_path))
