"""HMAC-SHA256 password hashing and verification using a server secret."""

__all__ = ("PasswordService",)

import bcrypt


class PasswordService:
    """Derive deterministic password digests for storage and comparison."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Return a lowercase hex digest of the password.

        Args:
            password (str): Plain text password to hash.

        Returns:
            str: Hex-encoded HMAC-SHA256 digest.

        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """Return whether the password matches the stored digest.

        Args:
            password (str): Plain text password to verify.
            hashed_password (str): Previously stored hex digest from ``hash_password``.

        Returns:
            bool: True if the digests are equal.

        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
