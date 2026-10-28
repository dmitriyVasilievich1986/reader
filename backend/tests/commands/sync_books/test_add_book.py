"""Tests for ``AddBookCommand``: folder validation, page parsing and persistence.

Uses the migrated SQLite fixtures and the ``make_book`` folder builder from
``commands.sync_books.conftest``.
"""

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from reader.commands.sync_books import AddBookCommand
from reader.config import AppConfig
from reader.services.daos import AuthorDAO, BookDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models import Author

from .conftest import MakeBook


class TestConvertBookName:
    """``convert_book_name`` turns a folder name into a book title."""

    @pytest.mark.parametrize(
        ("folder", "expected"),
        [
            ("alice_in_wonderland", "Alice in wonderland"),
            ("dune", "Dune"),
            ("THE_HOBBIT", "The hobbit"),
        ],
    )
    def test_converts_folder_name(self, folder: str, expected: str) -> None:
        """Replace underscores with spaces and capitalize the result.

        Args:
            folder (str): Book folder name.
            expected (str): Expected book title.

        Returns:
            None

        """
        assert AddBookCommand.convert_book_name(Path(folder)) == expected


class TestAddBookValidate:
    """``validate`` checks the folder and builds the book and its pages."""

    async def test_builds_book_and_sorted_pages(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Build pages from images only, sorted by position, with the first page as cover.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book(
            "lewis_carroll",
            "alice_in_wonderland",
            files=("page_2.PNG", "page_1.jpg", "page_3.webp", "notes.txt"),
        )
        (book_path / "extras").mkdir()
        author = Author(first_name="Lewis", last_name="Carroll")

        cmd = AddBookCommand(author=author, book_path=book_path, session=session, app_config=app_config)
        await cmd.initialize()
        await cmd.validate()

        assert cmd.book.name == "Alice in wonderland"
        assert cmd.book.author is author
        assert [p.position for p in cmd.pages] == [1, 2, 3]
        assert [p.cover for p in cmd.pages] == [
            "/static/images/lewis_carroll/alice_in_wonderland/page_1.jpg",
            "/static/images/lewis_carroll/alice_in_wonderland/page_2.PNG",
            "/static/images/lewis_carroll/alice_in_wonderland/page_3.webp",
        ]
        assert cmd.book.cover == cmd.pages[0].cover
        assert all(p.book is cmd.book for p in cmd.pages)

    async def test_strips_trailing_slash_from_static_url(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Build page URLs from ``static_url`` without a doubled slash.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book("lewis_carroll", "alice", files=("1.jpg",))

        cmd = AddBookCommand(
            author=Author(first_name="Lewis", last_name="Carroll"),
            book_path=book_path,
            static_url=" /media/ ",
            session=session,
            app_config=app_config,
        )
        await cmd.validate()

        assert cmd.pages[0].cover == "/media/lewis_carroll/alice/1.jpg"

    async def test_sorts_pages_numerically(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Sort ``page_10`` after ``page_2``.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book("lewis_carroll", "alice", files=("page_10.jpg", "page_2.jpg", "page_1.jpg"))

        cmd = AddBookCommand(
            author=Author(first_name="Lewis", last_name="Carroll"),
            book_path=book_path,
            session=session,
            app_config=app_config,
        )
        await cmd.validate()

        assert [p.position for p in cmd.pages] == [1, 2, 10]

    async def test_missing_folder_raises(self, app_config: AppConfig, library_path: Path) -> None:
        """Reject a book path that does not exist.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root without the requested book.

        Returns:
            None

        """
        cmd = AddBookCommand(author=Author(first_name="A"), book_path=library_path / "nope", app_config=app_config)

        with pytest.raises(ValueError, match="doesn't exists"):
            await cmd.validate()

    async def test_file_instead_of_folder_raises(self, app_config: AppConfig, library_path: Path) -> None:
        """Reject a book path that is a file.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Library root to create the file in.

        Returns:
            None

        """
        book_file = library_path / "book.jpg"
        book_file.touch()
        cmd = AddBookCommand(author=Author(first_name="A"), book_path=book_file, app_config=app_config)

        with pytest.raises(ValueError, match="is not a directory"):
            await cmd.validate()

    async def test_no_pages_raises(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Reject a book folder without any accepted image.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book("lewis_carroll", "alice", files=("readme.txt",))
        cmd = AddBookCommand(author=Author(first_name="A"), book_path=book_path, session=session, app_config=app_config)

        with pytest.raises(ValueError, match="does not contain any pages"):
            await cmd.validate()

    async def test_image_without_number_raises(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Reject an image whose name has no page number.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book("lewis_carroll", "alice", files=("page_1.jpg", "cover.jpg"))
        cmd = AddBookCommand(author=Author(first_name="A"), book_path=book_path, session=session, app_config=app_config)

        with pytest.raises(ValueError, match="does not have a valid number"):
            await cmd.validate()

    async def test_existing_book_raises(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Reject a book whose name already exists in the database.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        author = await AuthorDAO(session=session).create(first_name="Lewis", last_name="Carroll")
        await BookDAO(session=session).create(name="Alice", author_id=author.id)
        book_path = make_book("lewis_carroll", "alice")
        cmd = AddBookCommand(author=author, book_path=book_path, session=session, app_config=app_config)

        with pytest.raises(ValueError, match="already exists"):
            await cmd.validate()


class TestAddBookStr:
    """``str(command)`` previews the book and its pages."""

    def test_raises_before_validate(self, app_config: AppConfig, library_path: Path) -> None:
        """Refuse to render a command that was not validated.

        Args:
            app_config (AppConfig): Per-test configuration.
            library_path (pathlib.Path): Any folder path.

        Returns:
            None

        """
        cmd = AddBookCommand(author=Author(first_name="A"), book_path=library_path, app_config=app_config)

        with pytest.raises(ValueError, match="wasn't validated"):
            str(cmd)

    async def test_lists_book_and_pages(
        self,
        session: AsyncSession,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Render the book name and one line per page.

        Args:
            session (AsyncSession): Migrated-database session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book("lewis_carroll", "alice", files=("1.jpg", "2.jpg"))
        cmd = AddBookCommand(author=Author(first_name="A"), book_path=book_path, session=session, app_config=app_config)
        await cmd.validate()

        assert str(cmd) == (
            "Book:\n\tName: Alice\n\tPages:"
            "\n\t\t[1] - /static/images/lewis_carroll/alice/1.jpg"
            "\n\t\t[2] - /static/images/lewis_carroll/alice/2.jpg"
        )


class TestAddBookExecute:
    """``execute`` saves the book and its pages."""

    async def test_persists_book_for_existing_author(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Save the book with its pages and cover under an already saved author.

        Args:
            session (AsyncSession): Migrated-database session shared with the command.
            db_client (AsyncDatabaseClient): Factory for a separate read session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        author = await AuthorDAO(session=session).create(first_name="Lewis", last_name="Carroll")
        book_path = make_book("lewis_carroll", "alice", files=("page_1.jpg", "page_2.jpg"))
        cmd = AddBookCommand(author=author, book_path=book_path, session=session, app_config=app_config)
        await cmd.validate()
        await cmd.execute()

        async with db_client.session_factory() as read_session:
            book = await BookDAO(session=read_session).get_by_pk("Alice", "name")
            assert book.author.id == author.id
            assert book.cover == "/static/images/lewis_carroll/alice/page_1.jpg"
            assert sorted(p.position for p in book.pages) == [1, 2]

    async def test_opens_own_session_and_saves_new_author(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
        app_config: AppConfig,
        make_book: MakeBook,
    ) -> None:
        """Open a session when none is injected and save a new author with the book.

        Args:
            migrated_db (None): Side-effect fixture that upgrades the schema.
            db_client (AsyncDatabaseClient): Factory for a separate read session.
            app_config (AppConfig): Per-test configuration.
            make_book (MakeBook): Book folder factory.

        Returns:
            None

        """
        book_path = make_book("lewis_carroll", "alice", files=("page_1.jpg",))
        cmd = AddBookCommand(
            author=Author(first_name="Lewis", last_name="Carroll"),
            book_path=book_path,
            app_config=app_config,
        )
        await cmd.validate()
        await cmd.execute()

        async with db_client.session_factory() as read_session:
            book = await BookDAO(session=read_session).get_by_pk("Alice", "name")
            assert book.author.name == "Lewis Carroll"
            assert [p.position for p in book.pages] == [1]
