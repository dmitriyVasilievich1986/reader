"""Fixtures for ``sync_books`` command tests: migrated SQLite, a session and a library builder.

Mirrors the DAO-layer ``migrated_db`` / ``session`` fixtures so command tests
share schema setup without coupling to the daos conftest. ``make_book`` writes
a book folder of empty page images under a per-test library directory.
"""

from collections.abc import AsyncIterator, Callable
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.database import AsyncDatabaseClient

from ...conftest import ALEMBIC_INI

type MakeBook = Callable[..., Path]


@pytest.fixture
def migrated_db(
    monkeypatch: pytest.MonkeyPatch,
    test_config_file: Path,
    db_client: AsyncDatabaseClient,  # noqa: ARG001
) -> None:
    """Apply all Alembic migrations to the ephemeral SQLite database.

    Args:
        monkeypatch (pytest.MonkeyPatch): Sets ``CONFIG_FILE_PATH`` for Alembic.
        test_config_file (pathlib.Path): Same YAML path as parent ``AppConfig`` fixtures.
        db_client (AsyncDatabaseClient): Materialises the singleton before Alembic
            invokes application config.

    Returns:
        None

    """
    monkeypatch.setenv("CONFIG_FILE_PATH", str(test_config_file))
    command.upgrade(Config(str(ALEMBIC_INI)), "head")


@pytest.fixture
async def session(
    migrated_db: None,  # noqa: ARG001
    db_client: AsyncDatabaseClient,
) -> AsyncIterator[AsyncSession]:
    """Expose an ``AsyncSession`` against the migrated test database.

    Args:
        migrated_db (None): Side-effect fixture that upgrades schema before session use.
        db_client (AsyncDatabaseClient): Provides ``session_factory``.

    Yields:
        AsyncSession: Session closed after the test.

    """
    async with db_client.session_factory() as s:
        yield s


@pytest.fixture
def library_path(tmp_path: Path) -> Path:
    """Create an empty library folder for the current test.

    Args:
        tmp_path (pathlib.Path): Pytest-provided temporary directory unique to the test.

    Returns:
        pathlib.Path: Path to the created ``library`` folder.

    """
    path = tmp_path / "library"
    path.mkdir()
    return path


@pytest.fixture
def make_book(library_path: Path) -> MakeBook:
    """Return a factory that writes ``<library>/<author>/<book>/`` with the given files.

    Args:
        library_path (pathlib.Path): Library root that author folders are created in.

    Returns:
        MakeBook: Factory ``(author, book, files=("page_1.jpg", "page_2.jpg")) -> Path``
            returning the created book folder.

    """

    def _make_book(author: str, book: str, files: tuple[str, ...] = ("page_1.jpg", "page_2.jpg")) -> Path:
        """Create a book folder containing one empty file per name in ``files``.

        Args:
            author (str): Author folder name, e.g. ``lewis_carroll``.
            book (str): Book folder name, e.g. ``alice_in_wonderland``.
            files (tuple[str, ...], optional): File names to create in the book folder.
                Defaults to ``("page_1.jpg", "page_2.jpg")``.

        Returns:
            pathlib.Path: Path to the created book folder.

        """
        book_path = library_path / author / book
        book_path.mkdir(parents=True, exist_ok=True)
        for name in files:
            (book_path / name).touch()
        return book_path

    return _make_book
