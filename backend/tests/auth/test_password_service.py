"""Tests for ``PasswordService``: bcrypt hashing and verification.

Verifies that hashing is salted (non-deterministic), that the stored digest is
not the plaintext, and that ``check_password`` only accepts matching plaintext.
"""

from reader.services.auth import PasswordService


class TestPasswordServiceHash:
    """``hash_password`` returns a salted bcrypt digest."""

    def test_hash_password_is_not_plaintext(self) -> None:
        """The digest never matches the input password verbatim.

        Returns:
            None

        """
        password = "s3cret!"
        hashed = PasswordService.hash_password(password)
        assert hashed != password

    def test_hash_password_uses_random_salt(self) -> None:
        """Two calls on the same plaintext yield different digests.

        Returns:
            None

        """
        password = "same-password"
        first = PasswordService.hash_password(password)
        second = PasswordService.hash_password(password)
        assert first != second

    def test_hash_password_produces_bcrypt_digest_shape(self) -> None:
        """Output starts with a bcrypt identifier prefix and is reasonably long.

        Returns:
            None

        """
        hashed = PasswordService.hash_password("any-password")
        assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
        assert len(hashed) >= 59


class TestPasswordServiceCheck:
    """``check_password`` verifies plaintext against a previously stored digest."""

    def test_check_password_accepts_matching_plaintext(self) -> None:
        """Same plaintext as used for ``hash_password`` verifies as True.

        Returns:
            None

        """
        password = "correct horse battery staple"
        hashed = PasswordService.hash_password(password)
        assert PasswordService.check_password(password, hashed) is True

    def test_check_password_rejects_wrong_plaintext(self) -> None:
        """A different plaintext yields False.

        Returns:
            None

        """
        hashed = PasswordService.hash_password("alpha")
        assert PasswordService.check_password("beta", hashed) is False

    def test_check_password_is_case_sensitive(self) -> None:
        """Casing matters: ``Secret`` does not match a hash of ``secret``.

        Returns:
            None

        """
        hashed = PasswordService.hash_password("secret")
        assert PasswordService.check_password("Secret", hashed) is False

    def test_check_password_rejects_empty_string_against_real_hash(self) -> None:
        """Empty input does not match a hash of a real password.

        Returns:
            None

        """
        hashed = PasswordService.hash_password("not-empty")
        assert PasswordService.check_password("", hashed) is False

    def test_check_password_supports_unicode_plaintext(self) -> None:
        """Non-ASCII passwords round-trip through hash/check.

        Returns:
            None

        """
        password = "пароль-🔒"
        hashed = PasswordService.hash_password(password)
        assert PasswordService.check_password(password, hashed) is True
        assert PasswordService.check_password("пароль", hashed) is False
