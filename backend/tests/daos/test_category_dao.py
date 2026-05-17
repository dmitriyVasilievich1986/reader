"""Tests specific to ``CategoryDAO`` (eager-loaded ``books`` on single-row reads)."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.daos import AuthorDAO, BookDAO, CategoryDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models.category_book_table import CategoryBookTable


class TestCategoryDAO:
    """The Category DAO exposes ``books`` (many-to-many) as a single-row eager option."""

    async def test_get_by_pk_eagerly_loads_books(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Write through one session, then read through a fresh one to bypass the identity map."""
        write_authors = AuthorDAO(session=session)
        write_books = BookDAO(session=session)
        write_categories = CategoryDAO(session=session)

        author = await write_authors.create(first_name="Author")
        category = await write_categories.create(name="Mystery", description="Whodunits")
        book_a = await write_books.create(name="A Mystery", author_id=author.id)
        book_b = await write_books.create(name="B Mystery", author_id=author.id)

        session.add(CategoryBookTable(book_id=book_a.id, category_id=category.id))
        session.add(CategoryBookTable(book_id=book_b.id, category_id=category.id))
        await session.commit()

        async with db_client.session_factory() as read_session:
            read_categories = CategoryDAO(session=read_session)
            fetched = await read_categories.get_by_pk(category.id)
            assert {b.name for b in fetched.books} == {"A Mystery", "B Mystery"}

    async def test_unique_name_constraint_via_create(self, session: AsyncSession) -> None:
        """``name`` is unique — a second create with the same name should fail."""
        categories = CategoryDAO(session=session)
        await categories.create(name="Drama")

        with pytest.raises(IntegrityError):
            await categories.create(name="Drama")
