"""Tests for ``JWTTokenService``: token generation and decoding.

Covers the happy path (generate → decode round-trip), the supported algorithms,
expiry handling (``ExpiredSignatureError``), signature verification failures,
and the ``verify_signature=False`` escape hatch used for inspection.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, PyJWTError

from reader.services.auth import JWTTokenService
from reader.services.auth.models import AccessToken, JWTTokenMetadata

SECRET = "test-jwt-secret-key"


class TestGenerateToken:
    """``generate_token`` produces an ``AccessToken`` signed with the given secret."""

    def test_returns_access_token_with_signed_jwt(self) -> None:
        """The returned model carries a non-empty JWT and a future expiry.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET)
        before = datetime.now(timezone.utc)

        token = service.generate_token(user_id=42)

        assert isinstance(token, AccessToken)
        assert token.token
        assert token.expires_at > before

    def test_default_expiry_is_one_day_from_now(self) -> None:
        """Default lifetime is ~24 hours; allow a small clock-skew tolerance.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET)
        before = datetime.now(timezone.utc)

        token = service.generate_token(user_id=1)

        expected = before + timedelta(days=1)
        assert abs((token.expires_at - expected).total_seconds()) < 5

    def test_token_embeds_user_id_in_claims(self) -> None:
        """Decoding without going through the service still exposes ``user_id``.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET)
        token = service.generate_token(user_id=7)

        claims = jwt.decode(token.token, key=SECRET, algorithms=["HS256"])
        assert claims["user_id"] == 7


class TestDecodeToken:
    """``decode_token`` validates the signature and surfaces the structured claims."""

    def test_roundtrip_returns_matching_metadata(self) -> None:
        """A freshly issued token decodes back to the same ``user_id``.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET)
        issued = service.generate_token(user_id=99)

        metadata = service.decode_token(issued.token)

        assert isinstance(metadata, JWTTokenMetadata)
        assert metadata.user_id == 99
        assert abs((metadata.exp - issued.expires_at).total_seconds()) < 1

    def test_expired_token_raises_expired_signature_error(self) -> None:
        """A token whose ``exp`` is in the past raises ``ExpiredSignatureError``.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET)
        expired_payload = {
            "user_id": 1,
            "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
        }
        expired_token = jwt.encode(payload=expired_payload, key=SECRET, algorithm="HS256")

        with pytest.raises(ExpiredSignatureError):
            service.decode_token(expired_token)

    def test_wrong_secret_raises_invalid_signature(self) -> None:
        """A token signed with a different secret fails signature verification.

        Returns:
            None

        """
        issuing_service = JWTTokenService(secret_key="issuer-secret")
        verifying_service = JWTTokenService(secret_key="different-secret")

        issued = issuing_service.generate_token(user_id=5)

        with pytest.raises(InvalidSignatureError):
            verifying_service.decode_token(issued.token)

    def test_garbage_token_raises_pyjwt_error(self) -> None:
        """A malformed string is rejected by the JWT library as ``PyJWTError``.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET)

        with pytest.raises(PyJWTError):
            service.decode_token("not-a-real-jwt")

    def test_verify_signature_false_accepts_wrong_secret(self) -> None:
        """With ``verify_signature=False`` the secret no longer needs to match.

        Args:
            None

        Returns:
            None

        """
        issuer = JWTTokenService(secret_key="issuer-secret")
        inspector = JWTTokenService(secret_key="unrelated-secret")

        issued = issuer.generate_token(user_id=11)

        metadata = inspector.decode_token(issued.token, verify_signature=False)
        assert metadata.user_id == 11


class TestAlgorithmSelection:
    """The ``algorithm`` constructor argument flows into both encode and decode."""

    @pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
    def test_supported_hs_algorithms_round_trip(self, algorithm: str) -> None:
        """Each supported HS-family algorithm signs and verifies correctly.

        Args:
            algorithm (str): JWA name passed to the service constructor.

        Returns:
            None

        """
        service = JWTTokenService(secret_key=SECRET, algorithm=algorithm)
        issued = service.generate_token(user_id=3)

        metadata = service.decode_token(issued.token)
        assert metadata.user_id == 3

    def test_decoder_rejects_token_signed_with_different_algorithm(self) -> None:
        """A token signed with HS512 fails verification when the service expects HS256.

        Returns:
            None

        """
        hs512 = JWTTokenService(secret_key=SECRET, algorithm="HS512")
        hs256 = JWTTokenService(secret_key=SECRET, algorithm="HS256")

        issued = hs512.generate_token(user_id=2)

        with pytest.raises(PyJWTError):
            hs256.decode_token(issued.token)
