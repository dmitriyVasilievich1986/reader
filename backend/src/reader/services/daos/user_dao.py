"""DAO for creating and loading ``User`` records with hashed passwords."""

__all__ = ("UserDAO",)


from reader.services.auth import PasswordService
from reader.services.daos.base import BaseDAO
from reader.services.database.models.user import User


class UserDAO(BaseDAO[User]):
    """Persistence helpers for ``User`` rows, including password hashing on create."""

    database_model = User
    get_all_columns = (User.id, User.username, User.email)

    async def get_by_username(self, username: str) -> User:
        """Return the user with the given unique username.

        Args:
            username (str): Login name to resolve.

        Returns:
            User: Matching row from ``user``.

        """
        return await self.get_by_pk(username, "username")

    async def create(self, **kwargs) -> User:
        """Insert a user, replacing plaintext ``password`` with a keyed hash.

        Args:
            **kwargs: ``User`` column values. ``password`` must be plaintext; it
                is hashed with ``PasswordService`` before persistence.

        Returns:
            User: Newly created row.

        """
        hashed_password = PasswordService.hash_password(kwargs["password"])

        if self.session is not None:
            return await self._create_raw(self.session, **(kwargs | {"password": hashed_password}))

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._create_raw(session, **(kwargs | {"password": hashed_password}))
