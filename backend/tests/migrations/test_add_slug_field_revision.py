"""Tests for Alembic revision ``92552180df13`` — add ``book.slug``.

Exercises the fifth migration in isolation: upgrading from the prior revision
(``b922d12d33b3``) should add a NOT NULL ``slug`` column to ``book``, backfill
it from slugified names (with numeric suffixes for collisions and a
``book-<id>`` fallback for empty slugs), declare a unique constraint plus
index on ``slug``, and leave the dropped-and-recreated foreign keys
(``book.fk_author_id``, ``page.fk_book_id``) in place. Downgrading should
remove only ``slug`` and restore the same FKs.
"""

import sqlite3
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from .conftest import alembic_version, table_names

REVISION = "92552180df13"
PREVIOUS_REVISION = "b922d12d33b3"

NEW_COLUMN = "slug"
NEW_INDEX = "idx_book_slug"
NEW_UNIQUE_CONSTRAINT_TARGETS: frozenset[str] = frozenset({"slug"})
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
        "watches_count",
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


def _index_names(db_path: Path, table: str) -> set[str]:
    """Return all index names declared on ``table``.

    Args:
        db_path (pathlib.Path): SQLite file to inspect.
        table (str): Target table name.

    Returns:
        set[str]: Index names from ``PRAGMA index_list``.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        return {row[1] for row in conn.execute(f"PRAGMA index_list('{table}')").fetchall()}
    finally:
        conn.close()


def _foreign_key_targets(db_path: Path, table: str) -> set[tuple[str, str, str]]:
    """Return ``(referenced_table, from_column, to_column)`` triples for ``table``.

    Args:
        db_path (pathlib.Path): SQLite file to inspect.
        table (str): Table whose foreign keys to enumerate.

    Returns:
        set[tuple[str, str, str]]: One triple per declared FK.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(f"PRAGMA foreign_key_list('{table}')").fetchall()
    finally:
        conn.close()
    return {(row[2], row[3], row[4]) for row in rows}


def _seed_books(db_path: Path, names: list[str]) -> list[int]:
    """Insert one author and a book per ``names`` at the previous-revision schema.

    The previous revision predates the ``slug`` column, so books can be
    written by name alone. ``author_id`` is required (NOT NULL) and points at
    a single freshly-inserted author shared by every seeded book.

    Args:
        db_path (pathlib.Path): SQLite file already upgraded to
            ``PREVIOUS_REVISION``.
        names (list[str]): Book ``name`` values to insert in order.

    Returns:
        list[int]: Assigned ``book.id`` values in the same order as ``names``.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute(
            "INSERT INTO author (first_name, last_name) VALUES (?, ?)",
            ("Test", "Author"),
        )
        author_id = cur.lastrowid
        book_ids: list[int] = []
        for name in names:
            cur = conn.execute(
                "INSERT INTO book (name, author_id) VALUES (?, ?)",
                (name, author_id),
            )
            book_ids.append(int(cur.lastrowid))
        conn.commit()
        return book_ids
    finally:
        conn.close()


def _slug_by_book_id(db_path: Path) -> dict[int, str]:
    """Return a ``{book.id: book.slug}`` mapping read directly from SQLite.

    Args:
        db_path (pathlib.Path): SQLite file already upgraded to ``REVISION``.

    Returns:
        dict[int, str]: All rows in ``book`` keyed by primary key.

    """
    conn = sqlite3.connect(str(db_path))
    try:
        return {int(row[0]): row[1] for row in conn.execute("SELECT id, slug FROM book")}
    finally:
        conn.close()


@pytest.mark.migrations
class TestUpgradeToAddSlugRevision:
    """``alembic upgrade 92552180df13`` adds and backfills ``book.slug``."""

    def test_records_revision_in_alembic_version(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Persist ``92552180df13`` in ``alembic_version`` once applied.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert alembic_version(sqlite_db_path) == [REVISION]

    def test_book_has_slug_column(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Add ``slug`` to ``book``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        columns = {row[1] for row in _book_table_info(sqlite_db_path)}
        assert NEW_COLUMN in columns

    def test_slug_is_not_null(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Declare ``slug`` as NOT NULL after the backfill completes.

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
        assert bool(row[3]) is True, f"{NEW_COLUMN} should be NOT NULL"

    def test_slug_has_unique_constraint(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Enforce single-column uniqueness on ``slug``.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        uniques = _unique_columns(sqlite_db_path, "book")
        assert NEW_UNIQUE_CONSTRAINT_TARGETS.issubset(uniques)

    def test_slug_has_index(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Create the ``idx_book_slug`` index.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert NEW_INDEX in _index_names(sqlite_db_path, "book")

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

    def test_restores_book_author_foreign_key(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Re-create ``book.fk_author_id`` after the batch alteration.

        The migration must drop the FK before SQLite can rebuild ``book`` in
        batch mode; the upgrade is only sound if the FK comes back.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert ("author", "author_id", "id") in _foreign_key_targets(sqlite_db_path, "book")

    def test_restores_page_book_foreign_key(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Re-create ``page.fk_book_id`` after the batch alteration.

        ``page.fk_book_id`` is dropped so SQLite can rebuild ``book``; the
        migration must put it back.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)

        assert ("book", "book_id", "id") in _foreign_key_targets(sqlite_db_path, "page")

    def test_backfill_slugifies_existing_book_names(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Slugify each existing ``book.name`` into ``slug`` on upgrade.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, PREVIOUS_REVISION)
        [book_id] = _seed_books(sqlite_db_path, ["Hello, World!"])

        command.upgrade(alembic_config, REVISION)

        assert _slug_by_book_id(sqlite_db_path)[book_id] == "hello-world"

    def test_backfill_resolves_collisions_with_numeric_suffix(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Distinct names that slugify to the same base get ``-1``, ``-2``... suffixes.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, PREVIOUS_REVISION)
        book_ids = _seed_books(
            sqlite_db_path,
            ["Hello, World!", "Hello! World", "hello world"],
        )

        command.upgrade(alembic_config, REVISION)

        slugs = _slug_by_book_id(sqlite_db_path)
        assigned = {slugs[book_id] for book_id in book_ids}
        assert assigned == {"hello-world", "hello-world-1", "hello-world-2"}

    def test_backfill_falls_back_to_book_id_for_empty_slug(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Names whose slug is empty fall back to ``book-<id>``.

        Punctuation-only names like ``"!!!"`` slugify to the empty string;
        the migration's fallback gives them a deterministic, unique slug.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-upgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, PREVIOUS_REVISION)
        [book_id] = _seed_books(sqlite_db_path, ["!!!"])

        command.upgrade(alembic_config, REVISION)

        assert _slug_by_book_id(sqlite_db_path)[book_id] == f"book-{book_id}"


@pytest.mark.migrations
class TestDowngradeFromAddSlugRevision:
    """Downgrading from ``92552180df13`` only removes ``book.slug``."""

    def test_downgrade_removes_slug_column(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Drop ``slug`` when stepping back one revision.

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

    def test_downgrade_removes_slug_index(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Drop ``idx_book_slug`` on downgrade.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        assert NEW_INDEX not in _index_names(sqlite_db_path, "book")

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

    def test_downgrade_restores_book_author_foreign_key(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Re-create ``book.fk_author_id`` after the downgrade batch alteration.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        assert ("author", "author_id", "id") in _foreign_key_targets(sqlite_db_path, "book")

    def test_downgrade_restores_page_book_foreign_key(
        self,
        alembic_config: Config,
        sqlite_db_path: Path,
    ) -> None:
        """Re-create ``page.fk_book_id`` after the downgrade batch alteration.

        Args:
            alembic_config (Config): Alembic config bound to the test database.
            sqlite_db_path (pathlib.Path): SQLite file post-downgrade.

        Returns:
            None

        """
        command.upgrade(alembic_config, REVISION)
        command.downgrade(alembic_config, PREVIOUS_REVISION)

        assert ("book", "book_id", "id") in _foreign_key_targets(sqlite_db_path, "page")

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
