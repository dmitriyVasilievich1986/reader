"""DAO for the Book model."""

from datetime import datetime, timezone

__all__ = ("BookDAO",)

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.database.models.book import Book

from .base import BaseDAO


class BookDAO(BaseDAO[Book]):
    """DAO for the Book model."""

    database_model = Book
    get_all_columns = (
        Book.id,
        Book.name,
        Book.description,
        Book.cover,
        Book.author_id,
        Book.created_at,
        Book.updated_at,
        Book.watches_count,
        Book.slug,
    )
    select_in_options_single = (Book.author, Book.categories, Book.pages)
    select_in_options_all = (Book.author,)

    async def _increment_watches_count_raw(self, session: AsyncSession, book_id: int) -> None:
        """Increment ``watches_count`` by one for the row matching ``book_id``.

        Args:
            session (AsyncSession): Active async session.
            book_id (int): Book primary key.

        Returns:
            None

        Raises:
            NoResultFound: When no row matches ``book_id``.

        """
        result = await session.execute(
            update(Book)
            .where(Book.id == book_id)
            .values(
                watches_count=Book.watches_count + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        if result.rowcount == 0:  # type: ignore[attr-defined]
            raise NoResultFound()
        await session.commit()

    async def increment_watches_count(self, book_id: int) -> Book:
        """Atomically increment the watch counter and return the reloaded book.

        Performs ``SET watches_count = watches_count + 1`` in the database,
        then loads the row with the same relationship options as :meth:`get_by_pk`.

        Args:
            book_id (int): Book primary key.

        Returns:
            Book: Instance after increment, with relations loaded.

        Raises:
            NoResultFound: When no row matches ``book_id``.

        """
        if self.session is not None:
            await self._increment_watches_count_raw(self.session, book_id)
            return await self._get_by_pk_raw(self.session, book_id, self.pk_column_name)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            await self._increment_watches_count_raw(session, book_id)
            return await self._get_by_pk_raw(session, book_id, self.pk_column_name)
