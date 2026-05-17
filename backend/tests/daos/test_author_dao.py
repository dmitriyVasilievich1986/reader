"""Tests specific to ``AuthorDAO`` (eager-loaded ``books`` on single-row reads)."""

from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.daos import AuthorDAO, BookDAO
from reader.services.database import AsyncDatabaseClient


class TestAuthorDAO:
    """The Author DAO exposes ``books`` as a single-row eager option."""

    async def test_get_by_pk_eagerly_loads_books(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Write through one session, then read through a fresh one to bypass the identity map."""
        write_authors = AuthorDAO(session=session)
        write_books = BookDAO(session=session)

        author = await write_authors.create(first_name="Isaac", last_name="Asimov")
        await write_books.create(name="Foundation", author_id=author.id)
        await write_books.create(name="I, Robot", author_id=author.id)

        async with db_client.session_factory() as read_session:
            read_authors = AuthorDAO(session=read_session)
            fetched = await read_authors.get_by_pk(author.id)
            assert {b.name for b in fetched.books} == {"Foundation", "I, Robot"}

    async def test_get_all_does_not_require_books(self, session: AsyncSession) -> None:
        """``get_all`` uses ``load_only`` (no relationship eager-load); list works without books."""
        authors = AuthorDAO(session=session)
        await authors.create(first_name="Solo")
        rows, total = await authors.get_all()
        assert total == 1
        assert rows[0].first_name == "Solo"
