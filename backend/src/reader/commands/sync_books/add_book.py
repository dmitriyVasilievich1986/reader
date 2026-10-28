"""Command that adds one book folder of page images to the database."""

import re
from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from reader.config import AppConfig
from reader.services.daos import BookDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models import Author as AuthorDBModel, Book as BookDBModel, Page as PageDBModel

from ..base import BaseCommand


class AddBookCommand(BaseCommand[None]):
    """Add a book and its pages from a folder of numbered page images.

    The book name comes from the folder name; each image's first number in its
    file name is the page position. The first page becomes the book cover.

    Attributes:
        file_extensions (tuple[str, ...]): Image extensions accepted as pages.
        pages (list[PageDBModel]): Pages sorted by position; set by ``validate``.
        book (BookDBModel): New book; set by ``validate``.
        author (AuthorDBModel): Author the book belongs to.
        book_path (Path): Folder of the book.
        static_url (str): URL prefix used to build page image URLs, without a trailing slash.
        db_client (AsyncDatabaseClient): Database client used to open sessions.
        session (AsyncSession | None): Externally managed session, if any.
        book_dao (BookDAO): DAO for ``Book`` rows.

    """

    file_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp")
    pages: list[PageDBModel]
    book: BookDBModel

    def __init__(
        self,
        author: AuthorDBModel,
        book_path: Path | str,
        static_url: str = "/static/images",
        session: AsyncSession | None = None,
        app_config: AppConfig | None = None,
    ):
        """Store the book folder and author and set up database access.

        Args:
            author (AuthorDBModel): Author the book belongs to; may not be saved yet.
            book_path (Path | str): Book folder containing the page images.
            static_url (str, optional): URL prefix for page images. Defaults to "/static/images".
            session (AsyncSession | None, optional): Session to reuse instead of opening a new one.
                Defaults to None.
            app_config (AppConfig | None, optional): Application configuration; the global one is
                used when omitted. Defaults to None.

        Returns:
            None

        """
        self.author = author
        self.book_path = Path(book_path)
        self.static_url = static_url.strip().rstrip("/")

        app_config = app_config or AppConfig.get_or_create()
        self.db_client = AsyncDatabaseClient(app_config)
        self.session = session
        self.book_dao = (
            BookDAO(database_client=self.db_client, session=None)
            if session is None
            else BookDAO(database_client=None, session=session)
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
        """Return a human-readable summary of the book and its pages.

        Returns:
            str: Book name followed by each page's position and image URL.

        Raises:
            ValueError: If ``validate`` has not been run successfully.

        """
        if getattr(self, "pages", None) is None or getattr(self, "book", None) is None:
            raise ValueError("Command wasn't validated properly.")
        payload = f"Book:\n\tName: {self.book.name}\n\tPages:"
        for page in self.pages:
            payload += f"\n\t\t[{page.position}] - {page.cover}"
        return payload

    async def validate(self) -> None:
        """Check the book folder and build the book and its pages.

        Files that are not images with an accepted extension are logged and skipped.

        Returns:
            None

        Raises:
            ValueError: If the book path is missing or not a directory, a book with
                the same name already exists, an image name has no number, or the
                folder has no pages.

        """
        if not self.book_path.exists():
            raise ValueError("Folder doesn't exists.")
        if not self.book_path.is_dir():
            raise ValueError(f"Book path {self.book_path} is not a directory")

        book_name = self.convert_book_name(self.book_path)
        try:
            _ = await self.book_dao.get_by_pk(book_name, "name")
        except NoResultFound:
            pass
        else:
            raise ValueError(f"Book {book_name} already exists, path - {self.book_path}")

        self.book = BookDBModel(
            name=book_name,
            author=self.author,
        )
        pages: list[PageDBModel] = []
        for page_path in self.book_path.iterdir():
            if not page_path.is_file():
                logger.warning(f"Page path {page_path} is not a file. Skipping.")
                continue
            if page_path.suffix.lower() not in self.file_extensions:
                logger.warning(f"Page path {page_path} does not have a valid extension. Skipping.")
                continue
            if (page_index_reg := re.search(r"\d+", page_path.name)) is None:
                raise ValueError(f"Page path {page_path} does not have a valid number in the name")
            pages.append(
                PageDBModel(
                    position=int(page_index_reg.group(0)),
                    cover=f"{self.static_url}/{self.book_path.parent.name}/{self.book_path.name}/{page_path.name}",
                    book=self.book,
                )
            )

        if len(pages) == 0:
            raise ValueError(f"Book path {self.book_path} does not contain any pages")

        self.pages = sorted(pages, key=lambda p: p.position)
        self.book.cover = self.pages[0].cover

    @staticmethod
    def convert_book_name(book_path: Path) -> str:
        """Turn a book folder name into a book title.

        Underscores become spaces and the result is capitalized.

        Args:
            book_path (Path): Book folder, e.g. ``war_and_peace``.

        Returns:
            str: Book title, e.g. ``War and peace``.

        """
        return book_path.name.replace("_", " ").capitalize()

    async def _create(self, session: AsyncSession) -> None:
        """Add the book and its pages to the session and commit.

        Args:
            session (AsyncSession): Session used to add and commit the rows.

        Returns:
            None

        """
        session.add(self.book)
        session.add_all(self.pages)

    async def execute(self) -> None:
        """Save the book and its pages to the database.

        Uses the injected session when one was given, otherwise opens a new one.

        Returns:
            None

        """
        logger.info("Saving book and pages to DB")
        if self.session is not None:
            await self._create(self.session)
            await self.session.commit()
        else:
            async with self.db_client.session_factory() as session:
                await self._create(session)
                await session.commit()

        logger.info("Book is saved")
