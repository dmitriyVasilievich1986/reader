"""Tests for ``UserDAO`` behaviours around password hashing and username lookup.

Covers the password-hashing override on ``create`` (plaintext is replaced by a
``PasswordService`` digest before persistence), the ``get_by_username`` shortcut
over ``get_by_pk``, and database enforcement of unique ``username`` / ``email``.
Uses migrated SQLite fixtures from ``daos.conftest``.
"""

import pytest
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.auth import PasswordService
from reader.services.daos import UserDAO
from reader.services.database import AsyncDatabaseClient


class TestUserDAOCreate:
    """The User DAO hashes ``password`` before persistence on ``create``."""

    async def test_create_hashes_password(self, session: AsyncSession) -> None:
        """Store a bcrypt digest of ``password`` rather than the plaintext value.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        user = await users.create(
            username="alice",
            email="alice@example.com",
            password="s3cret",
        )

        assert user.password != "s3cret"
        assert PasswordService.check_password("s3cret", user.password)

    async def test_create_persists_profile_fields(self, session: AsyncSession) -> None:
        """Round-trip optional profile columns alongside the hashed password.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        user = await users.create(
            username="bob",
            email="bob@example.com",
            password="pw",
            first_name="Bob",
            last_name="Builder",
            is_admin=True,
        )

        assert user.id is not None
        assert user.first_name == "Bob"
        assert user.last_name == "Builder"
        assert user.is_admin is True
        assert user.is_active is True

    async def test_create_uses_db_client_path(
        self,
        migrated_db: None,  # noqa: ARG002
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Open a short-lived session from ``database_client`` and still hash the password.

        Args:
            migrated_db (None): Ensures migrated schema exists.
            db_client (AsyncDatabaseClient): Client-only DAO construction target.

        Returns:
            None

        """
        users = UserDAO(database_client=db_client)
        user = await users.create(
            username="carol",
            email="carol@example.com",
            password="pw",
        )

        assert user.id is not None
        assert PasswordService.check_password("pw", user.password)

    async def test_unique_username_constraint(self, session: AsyncSession) -> None:
        """Surface ``IntegrityError`` when inserting a duplicate ``username``.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        await users.create(username="dup", email="a@example.com", password="pw")

        with pytest.raises(IntegrityError):
            await users.create(username="dup", email="b@example.com", password="pw")

    async def test_unique_email_constraint(self, session: AsyncSession) -> None:
        """Surface ``IntegrityError`` when inserting a duplicate ``email``.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        await users.create(username="user_a", email="same@example.com", password="pw")

        with pytest.raises(IntegrityError):
            await users.create(username="user_b", email="same@example.com", password="pw")


class TestUserDAOGetByUsername:
    """``get_by_username`` resolves rows through the unique ``username`` column."""

    async def test_returns_user_for_existing_username(self, session: AsyncSession) -> None:
        """Return the row whose ``username`` matches the supplied value.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        created = await users.create(
            username="alice",
            email="alice@example.com",
            password="pw",
        )

        fetched = await users.get_by_username("alice")
        assert fetched.id == created.id
        assert fetched.email == "alice@example.com"

    async def test_raises_for_missing_username(self, session: AsyncSession) -> None:
        """Raise ``NoResultFound`` when no row matches the username.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        with pytest.raises(NoResultFound):
            await users.get_by_username("ghost")


class TestUserDAOGetAll:
    """``get_all`` lists users while restricting the loaded column set."""

    async def test_get_all_lists_users_without_password(self, session: AsyncSession) -> None:
        """Restrict listing payloads to ``id``, ``username``, and ``email`` via ``get_all_columns``.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        users = UserDAO(session=session)
        await users.create(username="alice", email="alice@example.com", password="pw")
        await users.create(username="bob", email="bob@example.com", password="pw")

        rows, total = await users.get_all(sort_by="username")
        assert total == 2
        assert [r.username for r in rows] == ["alice", "bob"]
        assert [r.email for r in rows] == ["alice@example.com", "bob@example.com"]
