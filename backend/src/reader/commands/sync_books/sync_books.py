"""Command that syncs a whole library folder of authors and books into the database."""

from pathlib import Path
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from reader.config import AppConfig
from reader.services.daos import BookDAO
from reader.services.database import AsyncDatabaseClient

from ..base import BaseCommand
from .add_author import AddAuthorCommand


class SyncBooksCommand(BaseCommand[None]):
    """Add every author found in a library folder, together with their books and pages.

    The library is expected to contain one sub-folder per author
    (``<first>_<last>``), each holding one sub-folder per book with page images.

    Attributes:
        authors (list[AddAuthorCommand]): Validated per-author commands; set by ``validate``.
        library_path (Path): Root folder of the library.
        static_url (str): URL prefix used to build page image URLs, without a trailing slash.
        app_config (AppConfig): Application configuration.
        db_client (AsyncDatabaseClient): Database client used to open sessions.
        session (AsyncSession | None): Externally managed session, if any.
        book_dao (BookDAO): DAO for ``Book`` rows.

    """

    authors: list[AddAuthorCommand]

    def __init__(
        self,
        library_path: Path | str,
        static_url: str = "/static/images",
        session: AsyncSession | None = None,
        app_config: AppConfig | None = None,
    ):
        """Store the library location and set up database access.

        Args:
            library_path (Path | str): Root folder containing one sub-folder per author.
            static_url (str, optional): URL prefix for page images. Defaults to "/static/images".
            session (AsyncSession | None, optional): Session to reuse instead of opening a new one.
                Defaults to None.
            app_config (AppConfig | None, optional): Application configuration; the global one is
                used when omitted. Defaults to None.

        Returns:
            None

        """
        self.library_path = Path(library_path)
        self.static_url = static_url.strip().rstrip("/")

        self.app_config = app_config or AppConfig.get_or_create()
        self.db_client = AsyncDatabaseClient(self.app_config)
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
        """Return a human-readable summary of all authors, books and pages to be added.

        Returns:
            str: One summary block per author, separated by newlines.

        Raises:
            ValueError: If ``validate`` has not been run successfully.

        """
        if getattr(self, "authors", None) is None:
            raise ValueError("Command wasn't validated properly.")
        return "\n".join(str(a) for a in self.authors)

    async def validate(self) -> None:
        """Check the library folder and build a validated ``AddAuthorCommand`` per author.

        Author folders that fail validation are logged and skipped.

        Returns:
            None

        Raises:
            ValueError: If the library path is missing or not a directory, or no
                author could be validated.

        """
        if not self.library_path.exists():
            raise ValueError("Library folder doesn't exists.")
        if not self.library_path.is_dir():
            raise ValueError(f"Library path {self.library_path} is not a directory")

        authors: list[AddAuthorCommand] = []
        for author_path in self.library_path.iterdir():
            cmd = AddAuthorCommand(
                author_path=author_path, session=self.session, static_url=self.static_url, app_config=self.app_config
            )
            try:
                await cmd.initialize()
                await cmd.validate()
                authors.append(cmd)
            except ValueError:
                logger.warning(f"Skipping author: {author_path}")

        if len(authors) == 0:
            raise ValueError("No Authors to add")

        self.authors = authors

    async def _create(self, session: AsyncSession) -> None:
        """Execute every author command and commit the session.

        Args:
            session (AsyncSession): Session to commit once all authors are saved.

        Returns:
            None

        """
        for author in self.authors:
            await author._create(session=session)  # noqa: SLF001

    async def execute(self) -> None:
        """Save all validated authors, books and pages to the database.

        Uses the injected session when one was given, otherwise opens a new one.

        Returns:
            None

        """
        logger.info("Saving authors and books to DB")
        if self.session is not None:
            await self._create(self.session)
            await self.session.commit()
        else:
            async with self.db_client.session_factory() as session:
                await self._create(session)
                await session.commit()

        logger.info("Authors are saved")
