"""Tests for ``AddAuthorCommand``: author resolution, book discovery and persistence.

Uses the migrated SQLite fixtures and the ``make_book`` folder builder from
``commands.sync_books.conftest``.
"""

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from reader.commands.sync_books import AddAuthorCommand
from reader.config import AppConfig
from reader.services.daos import AuthorDAO, BookDAO
from reader.services.database import AsyncDatabaseClient

from .conftest import MakeBook


class TestGetAuthorName:
    """``get_author_name`` splits an author folder name into first and last names."""

    @pytest.mark.parametrize(
        ("folder", "expected"),
        [
            ("lewis_carroll", ("Lewis", "Carroll")),
            ("LEWIS_CARROLL", ("Lewis", "Carroll")),
            ("antoine_de_saint-exupery", ("Antoine", "De_saint-exupery")),
        ],
    )
    def test_splits_on_first_underscore(self, folder: str, expected: tuple[str, str]) -> None:
        """Split on the first ``_`` and capitalize both parts.

        Args:
            folder (str): Author folder name.
            expected (tuple[str, str]): Expected first and last names.

        Returns:
            None

        """
        assert AddAuthorCommand.get_author_name(Path(folder)) == expected

    def test_name_without_last_name(self) -> None:
        """Return ``None`` as the last name when the folder has no ``_``.

        Returns:
            None

        """
        assert AddAuthorCommand.get_author_name(Path("plato")) == ("Plato", None)


class TestAddAuthorValidate:
    """``validate`` resolves the author and builds one command per valid book folder."""

    async def test_builds_new_author_and_skips_invalid_books(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Create an unsaved author and keep only book folders that validate.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        make_book("lewis_carroll", "alice")
        make_book("lewis_carroll", "sylvie_and_bruno")
        make_book("lewis_carroll", "empty_book", files=())
        (library_path / "lewis_carroll" / "notes.txt").touch()

        cmd = AddAuthorCommand(author_path=library_path / "lewis_carroll", session=session, app_config=app_config)
        await cmd.initialize()
        await cmd.validate()

        assert cmd.author.id is None
        assert (cmd.author.first_name, cmd.author.last_name) == ("Lewis", "Carroll")
        assert sorted(b.book.name for b in cmd.books) == ["Alice", "Sylvie and bruno"]
        assert all(b.book.author is cmd.author for b in cmd.books)

    async def test_reuses_existing_author(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Use the saved author whose first and last name match the folder.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        existing = await AuthorDAO(session=session).create(first_name="Lewis", last_name="Carroll")
        make_book("lewis_carroll", "alice")

        cmd = AddAuthorCommand(author_path=library_path / "lewis_carroll", session=session, app_config=app_config)
        await cmd.validate()

        assert cmd.author.id == existing.id

    async def test_builds_author_without_last_name(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Create an author with no last name from a folder name without ``_``.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        make_book("plato", "republic")

        cmd = AddAuthorCommand(author_path=library_path / "plato", session=session, app_config=app_config)
        await cmd.validate()

        assert cmd.author.id is None
        assert (cmd.author.first_name, cmd.author.last_name) == ("Plato", None)

    async def test_reuses_existing_author_without_last_name(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Use the saved author with no last name when the folder name has no ``_``.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        existing = await AuthorDAO(session=session).create(first_name="Plato", last_name=None)
        make_book("plato", "republic")

        cmd = AddAuthorCommand(author_path=library_path / "plato", session=session, app_config=app_config)
        await cmd.validate()

        assert cmd.author.id == existing.id

    async def test_no_valid_books_raises(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Reject an author folder where no book folder validates.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        make_book("lewis_carroll", "empty_book", files=())

        cmd = AddAuthorCommand(author_path=library_path / "lewis_carroll", session=session, app_config=app_config)

        with pytest.raises(ValueError, match="No books to add"):
            await cmd.validate()

    async def test_missing_folder_raises(self, app_config: AppConfig, library_path: Path) -> None:
        """Reject an author path that does not exist.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root without the requested author.

        Returns:
            None

        """
        cmd = AddAuthorCommand(author_path=library_path / "nobody", app_config=app_config)

        with pytest.raises(ValueError, match="doesn't exists"):
            await cmd.validate()

    async def test_file_instead_of_folder_raises(self, app_config: AppConfig, library_path: Path) -> None:
        """Reject an author path that is a file.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root to create the file in.

        Returns:
            None

        """
        author_file = library_path / "lewis_carroll"
        author_file.touch()
        cmd = AddAuthorCommand(author_path=author_file, app_config=app_config)

        with pytest.raises(ValueError, match="is not a directory"):
            await cmd.validate()


class TestAddAuthorStr:
    """``str(command)`` previews the author and their books."""

    def test_raises_before_validate(self, app_config: AppConfig, library_path: Path) -> None:
        """Refuse to render a command that was not validated.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Any folder path.

        Returns:
            None

        """
        cmd = AddAuthorCommand(author_path=library_path, app_config=app_config)

        with pytest.raises(ValueError, match="wasn't validated"):
            str(cmd)

    async def test_lists_author_and_books(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Render the author name followed by each book preview.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        make_book("lewis_carroll", "alice", files=("1.jpg",))

        cmd = AddAuthorCommand(author_path=library_path / "lewis_carroll", session=session, app_config=app_config)
        await cmd.validate()

        assert str(cmd) == (
            "Author:\n\tName: Lewis Carroll\nBook:\n\tName: Alice\n\tPages:"
            "\n\t\t[1] - /static/images/lewis_carroll/alice/1.jpg"
        )


class TestAddAuthorExecute:
    """``execute`` saves the author and all of their books."""

    async def test_persists_new_author_with_books(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Save a new author together with every valid book and its pages.

        Args:
            session (AsyncSession): Migrated-database session shared with the command.
            db_client (AsyncDatabaseClient): Factory for a separate read session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        make_book("lewis_carroll", "alice", files=("1.jpg", "2.jpg"))
        make_book("lewis_carroll", "sylvie_and_bruno", files=("1.jpg",))

        cmd = AddAuthorCommand(author_path=library_path / "lewis_carroll", session=session, app_config=app_config)
        await cmd.validate()
        await cmd.execute()

        async with db_client.session_factory() as read_session:
            authors, count = await AuthorDAO(session=read_session).get_all()
            assert count == 1
            author = await AuthorDAO(session=read_session).get_by_pk(authors[0].id)
            assert author.name == "Lewis Carroll"
            assert sorted(b.name for b in author.books) == ["Alice", "Sylvie and bruno"]
            alice = await BookDAO(session=read_session).get_by_pk("Alice", "name")
            assert len(alice.pages) == 2

    async def test_does_not_duplicate_existing_author(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
        app_config: AppConfig,
        make_book: MakeBook,
        library_path: Path,
    ) -> None:
        """Attach new books to the saved author instead of creating another one.

        Args:
            session (AsyncSession): Migrated-database session shared with the command.
            db_client (AsyncDatabaseClient): Factory for a separate read session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.
            library_path (pathlib.Path): Library root holding the author folder.

        Returns:
            None

        """
        existing = await AuthorDAO(session=session).create(first_name="Lewis", last_name="Carroll")
        make_book("lewis_carroll", "alice")

        cmd = AddAuthorCommand(author_path=library_path / "lewis_carroll", session=session, app_config=app_config)
        await cmd.validate()
        await cmd.execute()

        async with db_client.session_factory() as read_session:
            _, count = await AuthorDAO(session=read_session).get_all()
            assert count == 1
            book = await BookDAO(session=read_session).get_by_pk("Alice", "name")
            assert book.author.id == existing.id
