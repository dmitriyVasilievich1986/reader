"""Tests for ``SyncBooksCommand``: library validation and syncing every author.

Uses the migrated SQLite fixtures and the ``make_book`` folder builder from
``commands.sync_books.conftest``.
"""

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from reader.commands.sync_books import SyncBooksCommand
from reader.config import AppConfig
from reader.services.daos import AuthorDAO, BookDAO
from reader.services.database import AsyncDatabaseClient

from .conftest import MakeBook


class TestSyncBooksValidate:
    """``validate`` checks the library folder and builds one command per valid author."""

    async def test_builds_authors_and_skips_invalid_ones(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Keep only author folders that validate.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root passed to the command.

        Returns:
            None

        """
        make_book("lewis_carroll", "alice")
        make_book("frank_herbert", "dune")
        (library_path / "no_books").mkdir()

        cmd = SyncBooksCommand(library_path=library_path, session=session, app_config=app_config)
        await cmd.initialize()
        await cmd.validate()

        assert sorted(a.author.name for a in cmd.authors) == ["Frank Herbert", "Lewis Carroll"]

    async def test_no_valid_authors_raises(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        library_path: Path,
    ) -> None:
        """Reject a library where no author folder validates.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root passed to the command.

        Returns:
            None

        """
        (library_path / "no_books").mkdir()

        cmd = SyncBooksCommand(library_path=library_path, session=session, app_config=app_config)

        with pytest.raises(ValueError, match="No Authors to add"):
            await cmd.validate()

    async def test_missing_folder_raises(self, app_config: AppConfig, library_path: Path) -> None:
        """Reject a library path that does not exist.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Existing library root used to build a missing path.

        Returns:
            None

        """
        cmd = SyncBooksCommand(library_path=library_path / "missing", app_config=app_config)

        with pytest.raises(ValueError, match="doesn't exists"):
            await cmd.validate()

    async def test_file_instead_of_folder_raises(self, app_config: AppConfig, library_path: Path) -> None:
        """Reject a library path that is a file.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root to create the file in.

        Returns:
            None

        """
        library_file = library_path / "library.txt"
        library_file.touch()
        cmd = SyncBooksCommand(library_path=library_file, app_config=app_config)

        with pytest.raises(ValueError, match="is not a directory"):
            await cmd.validate()


class TestSyncBooksStr:
    """``str(command)`` previews every author."""

    def test_raises_before_validate(self, app_config: AppConfig, library_path: Path) -> None:
        """Refuse to render a command that was not validated.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root passed to the command.

        Returns:
            None

        """
        cmd = SyncBooksCommand(library_path=library_path, app_config=app_config)

        with pytest.raises(ValueError, match="wasn't validated"):
            str(cmd)


class TestSyncBooksExecute:
    """``execute`` saves every author, book and page in the library."""

    async def test_persists_whole_library(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Save all authors and their books.

        Args:
            session (AsyncSession): Migrated-database session shared with the command.
            db_client (AsyncDatabaseClient): Factory for a separate read session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root passed to the command.

        Returns:
            None

        """
        make_book("lewis_carroll", "alice")
        make_book("lewis_carroll", "sylvie_and_bruno")
        make_book("frank_herbert", "dune")

        cmd = SyncBooksCommand(library_path=library_path, session=session, app_config=app_config)
        await cmd.validate()
        await cmd.execute()

        async with db_client.session_factory() as read_session:
            _, authors_count = await AuthorDAO(session=read_session).get_all()
            books, books_count = await BookDAO(session=read_session).get_all()
            assert authors_count == 2
            assert books_count == 3
            assert sorted(b.name for b in books) == ["Alice", "Dune", "Sylvie and bruno"]
