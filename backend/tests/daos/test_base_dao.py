"""Tests for ``BaseDAO`` CRUD, filtering, pagination, and session/client paths.

Uses ``AuthorDAO`` as the concrete subject because ``BaseDAO`` itself is abstract;
coverage targets shared ``BaseDAO`` logic. Fixtures come from ``daos.conftest``
(migrated schema and ``AsyncSession``).
"""

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.daos import AuthorDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models.author import Author


class TestInit:
    """``BaseDAO.__init__`` requires at least one of ``database_client`` or ``session``."""

    def test_raises_when_neither_is_provided(self) -> None:
        """Reject construction when neither client nor session is supplied.

        Returns:
            None

        """
        with pytest.raises(ValueError, match="Either database_client or session"):
            AuthorDAO(database_client=None, session=None)

    def test_stores_session_when_provided(self, session: AsyncSession) -> None:
        """Retain injected ``AsyncSession`` and leave ``database_client`` unset.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        assert dao.session is session
        assert dao.database_client is None

    def test_stores_database_client_when_provided(
        self,
        db_client: AsyncDatabaseClient,
        migrated_db: None,  # noqa: ARG002
    ) -> None:
        """Retain injected ``AsyncDatabaseClient`` and leave ``session`` unset until use.

        Args:
            db_client (AsyncDatabaseClient): Shared SQLite client singleton.
            migrated_db (None): Ensures Alembic ``upgrade head`` ran before DAO use.

        Returns:
            None

        """
        dao = AuthorDAO(database_client=db_client)
        assert dao.database_client is db_client
        assert dao.session is None


class TestConcatFilters:
    """Combines ``base_filters`` with caller-supplied filters; converts dicts to expressions."""

    def test_returns_empty_list_when_no_filters_present(self, session: AsyncSession) -> None:
        """Yield no expressions when caller passes no filters and ``base_filters`` is empty.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        assert dao.concat_filters(None) == []

    def test_includes_base_filters_when_set(self, session: AsyncSession) -> None:
        """Prepend DAO-level ``base_filters`` when caller supplies none.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        base = [Author.first_name == "X"]
        dao.base_filters = base
        try:
            assert dao.concat_filters(None) == base
        finally:
            dao.base_filters = None

    def test_passes_through_column_element_filters(self, session: AsyncSession) -> None:
        """Leave SQLAlchemy column expressions untouched.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        expr = Author.first_name == "Alice"
        result = dao.concat_filters([expr])
        assert result == [expr]

    def test_converts_dict_filter_to_expression(self, session: AsyncSession) -> None:
        """Coerce declarative dict filters into ORM-compatible expressions.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        result = dao.concat_filters([{"column": "first_name", "operator": "eq", "value": "Alice"}])
        assert len(result) == 1
        compiled = str(result[0].compile(compile_kwargs={"literal_binds": True}))
        assert compiled == "author.first_name = 'Alice'"

    def test_mix_of_dicts_and_expressions(self, session: AsyncSession) -> None:
        """Preserve order when chaining expression and dict filters.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        expr = Author.id > 0
        result = dao.concat_filters(
            [expr, {"column": "first_name", "operator": "eq", "value": "X"}],
        )
        assert len(result) == 2


class TestCreate:
    """``create`` persists a row and reloads it via ``get_by_pk``."""

    async def test_create_persists_and_assigns_pk(self, session: AsyncSession) -> None:
        """Insert an author row and populate primary key on the returned model.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        author = await dao.create(first_name="Alice", last_name="Smith")
        assert author.id is not None
        assert author.first_name == "Alice"
        assert author.last_name == "Smith"

    async def test_create_uses_db_client_path(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Open short-lived sessions from ``database_client`` when none is injected.

        Args:
            migrated_db (None): Ensures migrated schema exists.
            db_client (AsyncDatabaseClient): Client-only DAO construction target.

        Returns:
            None

        """
        dao = AuthorDAO(database_client=db_client)
        author = await dao.create(first_name="Bob")
        assert author.id is not None


class TestGetByPk:
    """``get_by_pk`` returns the matching row and supports extra filters."""

    async def test_returns_row_for_existing_pk(self, session: AsyncSession) -> None:
        """Load the author persisted under the supplied primary key.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        created = await dao.create(first_name="Alice")
        fetched = await dao.get_by_pk(created.id)
        assert fetched.id == created.id
        assert fetched.first_name == "Alice"

    async def test_raises_for_missing_pk(self, session: AsyncSession) -> None:
        """Raise ``NoResultFound`` when no row matches the pk.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        with pytest.raises(NoResultFound):
            await dao.get_by_pk(99999)

    async def test_extra_filter_can_exclude_the_row(self, session: AsyncSession) -> None:
        """Apply additional predicates so logically missing rows yield ``NoResultFound``.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        created = await dao.create(first_name="Alice")
        with pytest.raises(NoResultFound):
            await dao.get_by_pk(
                created.id,
                filters=[{"column": "first_name", "operator": "eq", "value": "Other"}],
            )

    async def test_get_by_pk_uses_db_client_path(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Resolve ``get_by_pk`` via internal session management on client-backed DAO.

        Args:
            migrated_db (None): Ensures migrated schema exists.
            db_client (AsyncDatabaseClient): Client-only DAO construction target.

        Returns:
            None

        """
        dao = AuthorDAO(database_client=db_client)
        created = await dao.create(first_name="Carol")
        fetched = await dao.get_by_pk(created.id)
        assert fetched.id == created.id


class TestGetTotal:
    """``get_total`` counts rows and respects optional filters."""

    async def test_counts_all_rows(self, session: AsyncSession) -> None:
        """Include every persisted author row in the unconditional count.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await dao.create(first_name="A")
        await dao.create(first_name="B")
        await dao.create(first_name="C")
        assert await dao.get_total() == 3

    async def test_filters_narrow_the_count(self, session: AsyncSession) -> None:
        """Restrict aggregate count to rows matching declarative filters.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await dao.create(first_name="Alice")
        await dao.create(first_name="Bob")
        total = await dao.get_total(
            filters=[{"column": "first_name", "operator": "eq", "value": "Alice"}],
        )
        assert total == 1


class TestGetAll:
    """``get_all`` returns ``(rows, total)`` and applies sorting, pagination, filters."""

    async def _seed(self, dao: AuthorDAO) -> list[Author]:
        """Insert three deterministic authors used across list-pagination tests.

        Args:
            dao (AuthorDAO): DAO backed by current test ``AsyncSession``.

        Returns:
            list[Author]: Created rows in insertion order ``Carol``, ``Alice``, ``Bob``.

        """
        return [
            await dao.create(first_name="Carol"),
            await dao.create(first_name="Alice"),
            await dao.create(first_name="Bob"),
        ]

    async def test_returns_rows_and_total(self, session: AsyncSession) -> None:
        """Return distinct page slice and cardinality matching full table contents.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await self._seed(dao)
        rows, total = await dao.get_all()
        assert total == 3
        assert {row.first_name for row in rows} == {"Alice", "Bob", "Carol"}

    async def test_sort_ascending(self, session: AsyncSession) -> None:
        """Sort ``first_name`` ascending lexicographically.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await self._seed(dao)
        rows, _ = await dao.get_all(sort_by="first_name", sort_order="asc")
        assert [r.first_name for r in rows] == ["Alice", "Bob", "Carol"]

    async def test_sort_descending(self, session: AsyncSession) -> None:
        """Sort ``first_name`` descending lexicographically.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await self._seed(dao)
        rows, _ = await dao.get_all(sort_by="first_name", sort_order="desc")
        assert [r.first_name for r in rows] == ["Carol", "Bob", "Alice"]

    async def test_pagination_limit_and_offset(self, session: AsyncSession) -> None:
        """Apply ``LIMIT`` / ``OFFSET`` after stable sort so middle row is selectable.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await self._seed(dao)
        rows, total = await dao.get_all(limit=1, offset=1, sort_by="first_name")
        assert total == 3
        assert len(rows) == 1
        assert rows[0].first_name == "Bob"

    async def test_filter_dict_narrows_results(self, session: AsyncSession) -> None:
        """Apply dict filters identical to counting helpers for bounded result sets.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        await self._seed(dao)
        rows, total = await dao.get_all(
            filters=[{"column": "first_name", "operator": "eq", "value": "Alice"}],
        )
        assert total == 1
        assert rows[0].first_name == "Alice"

    async def test_get_all_uses_db_client_path(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
    ) -> None:
        """List authors through internally managed sessions on client-backed DAO.

        Args:
            migrated_db (None): Ensures migrated schema exists.
            db_client (AsyncDatabaseClient): Client-only DAO construction target.

        Returns:
            None

        """
        dao = AuthorDAO(database_client=db_client)
        await dao.create(first_name="OnlyOne")
        rows, total = await dao.get_all()
        assert total == 1
        assert rows[0].first_name == "OnlyOne"


class TestUpdate:
    """``update`` applies kwargs and reloads; no-kwargs returns the row unchanged."""

    async def test_updates_fields(self, session: AsyncSession) -> None:
        """Persist partial field mutations and reload merged state.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        author = await dao.create(first_name="Old", last_name="Name")
        updated = await dao.update(author.id, first_name="New")
        assert updated.first_name == "New"
        assert updated.last_name == "Name"

    async def test_no_kwargs_returns_existing_row(self, session: AsyncSession) -> None:
        """Treat empty updates as reload-by-id semantics.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        author = await dao.create(first_name="Alice")
        result = await dao.update(author.id)
        assert result.id == author.id
        assert result.first_name == "Alice"

    async def test_update_uses_db_client_path(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Persist updates via short-lived sessions on client-backed DAO.

        Args:
            migrated_db (None): Ensures migrated schema exists.
            db_client (AsyncDatabaseClient): Client-only DAO construction target.

        Returns:
            None

        """
        dao = AuthorDAO(database_client=db_client)
        author = await dao.create(first_name="Old")
        updated = await dao.update(author.id, first_name="New")
        assert updated.first_name == "New"


class TestDelete:
    """``delete`` removes the row and returns True."""

    async def test_deletes_existing_row(self, session: AsyncSession) -> None:
        """Remove a row by pk and forbid subsequent reload.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        author = await dao.create(first_name="Alice")
        assert await dao.delete(author.id) is True
        with pytest.raises(NoResultFound):
            await dao.get_by_pk(author.id)

    async def test_delete_missing_pk_raises(self, session: AsyncSession) -> None:
        """Surface ``NoResultFound`` when delete targets absent pk.

        Args:
            session (AsyncSession): Test session fixture.

        Returns:
            None

        """
        dao = AuthorDAO(session=session)
        with pytest.raises(NoResultFound):
            await dao.delete(99999)

    async def test_delete_uses_db_client_path(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Delete rows through internally managed sessions on client-backed DAO.

        Args:
            migrated_db (None): Ensures migrated schema exists.
            db_client (AsyncDatabaseClient): Client-only DAO construction target.

        Returns:
            None

        """
        dao = AuthorDAO(database_client=db_client)
        author = await dao.create(first_name="Alice")
        assert await dao.delete(author.id) is True
