"""Command that adds one author folder, with its books, to the database."""

from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from reader.config import AppConfig
from reader.services.daos import AuthorDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models import Author as AuthorDBModel

from ..base import BaseCommand
from .add_book import AddBookCommand


class AddAuthorCommand(BaseCommand[None]):
    """Add an author from a ``<first>_<last>`` folder, along with every book folder inside it.

    An existing author with the same name is reused; otherwise a new one is created.

    Attributes:
        author (AuthorDBModel): Existing or new author; set by ``validate``.
        books (list[AddBookCommand]): Validated per-book commands; set by ``validate``.
        author_path (Path): Folder of the author.
        static_url (str): URL prefix used to build page image URLs, without a trailing slash.
        app_config (AppConfig): Application configuration.
        db_client (AsyncDatabaseClient): Database client used to open sessions.
        session (AsyncSession | None): Externally managed session, if any.
        author_dao (AuthorDAO): DAO for ``Author`` rows.

    """

    author: AuthorDBModel
    books: list[AddBookCommand]

    def __init__(
        self,
        author_path: Path | str,
        static_url: str = "/static/images",
        session: AsyncSession | None = None,
        app_config: AppConfig | None = None,
    ):
        """Store the author folder and set up database access.

        Args:
            author_path (Path | str): Author folder named ``<first>_<last>`` with one sub-folder per book.
            static_url (str, optional): URL prefix for page images. Defaults to "/static/images".
            session (AsyncSession | None, optional): Session to reuse instead of opening a new one.
                Defaults to None.
            app_config (AppConfig | None, optional): Application configuration; the global one is
                used when omitted. Defaults to None.

        Returns:
            None

        """
        self.author_path = Path(author_path)
        self.static_url = static_url.strip().rstrip("/")

        self.app_config = app_config or AppConfig.get_or_create()
        self.db_client = AsyncDatabaseClient(self.app_config)
        self.session = session
        self.author_dao = (
            AuthorDAO(database_client=self.db_client, session=None)
            if session is None
            else AuthorDAO(database_client=None, session=session)
        )

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize the command.

        Args:
            **kwargs (Any): Unused keyword arguments retained for ``BaseCommand`` compatibility.

        Returns:
            None

        """
        pass

    def __str__(self) -> str:
        """Return a human-readable summary of the author and their books.

        Returns:
            str: Author name followed by each book's summary.

        Raises:
            ValueError: If ``validate`` has not been run successfully.

        """
        if getattr(self, "author", None) is None or getattr(self, "books", None) is None:
            raise ValueError("Command wasn't validated properly.")
        payload = f"Author:\n\tName: {self.author.name}"
        for book in self.books:
            payload += f"\n{book}"
        return payload

    async def validate(self) -> None:
        """Resolve the author and build a validated ``AddBookCommand`` per book folder.

        Book folders that fail validation are logged and skipped.

        Returns:
            None

        Raises:
            ValueError: If the author path is missing or not a directory, more than
                one author matches the name, or no book could be validated.

        """
        if not self.author_path.exists():
            raise ValueError("Author folder doesn't exists.")
        if not self.author_path.is_dir():
            raise ValueError(f"Author path {self.author_path} is not a directory")

        first_name, last_name = self.get_author_name(self.author_path)
        authors, authors_count = await self.author_dao.get_all(
            filters=[AuthorDBModel.first_name == first_name, AuthorDBModel.last_name == last_name]
        )
        if authors_count > 1:
            raise ValueError("Couldn't find distinct author")
        if authors_count == 1:
            self.author = authors[0]
        else:
            self.author = AuthorDBModel(
                first_name=first_name,
                last_name=last_name,
            )

        books: list[AddBookCommand] = []
        for book_path in self.author_path.iterdir():
            cmd = AddBookCommand(
                book_path=book_path,
                author=self.author,
                session=self.session,
                static_url=self.static_url,
                app_config=self.app_config,
            )
            try:
                await cmd.initialize()
                await cmd.validate()
                books.append(cmd)
            except ValueError:
                logger.warning(f"Skipping book: {book_path}")

        if len(books) == 0:
            raise ValueError("No books to add")

        self.books = books

    @staticmethod
    def get_author_name(author_path: Path) -> tuple[str, str | None]:
        """Split an author folder name into capitalized first and last names.

        The folder name is split on the first ``_``; a name without ``_`` has no last name.

        Args:
            author_path (Path): Author folder, e.g. ``john_smith``.

        Returns:
            tuple[str, str | None]: First name and last name (None when absent).

        """
        names = author_path.name.split("_", maxsplit=1)
        first_name = names[0]
        last_name = None if len(names) == 1 else names[1]
        last_name_capital = last_name and last_name.capitalize()
        return first_name.capitalize(), last_name_capital

    async def _create(self, session: AsyncSession) -> None:
        """Add the author if new, execute every book command and commit the session.

        Args:
            session (AsyncSession): Session used to add the author and commit.

        Returns:
            None

        """
        if self.author.id is None:
            session.add(self.author)

        for book in self.books:
            await book._create(session=session)  # noqa: SLF001

    async def execute(self) -> None:
        """Save the author and their books to the database.

        Uses the injected session when one was given, otherwise opens a new one.

        Returns:
            None

        """
        logger.info("Saving author and books to DB")
        if self.session is not None:
            await self._create(self.session)
            await self.session.commit()
        else:
            async with self.db_client.session_factory() as session:
                await self._create(session)
                await session.commit()

        logger.info("Author is saved")
