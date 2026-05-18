"""Encode and decode JWT access tokens with user identity and expiry."""

__all__ = ("JWTTokenService",)

from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from jwt.types import Options

from .models import AccessToken, JWTTokenMetadata


class JWTTokenService:
    """Build and verify signed JWTs using a shared secret and algorithm."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Initialize the service with signing parameters.

        Args:
            secret_key (str): Symmetric key used to sign and verify tokens.
            algorithm (str, optional): JWA algorithm name. Defaults to "HS256".

        """
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, user_id: int) -> AccessToken:
        """Create a new JWT for the given user with a one-day lifetime.

        Args:
            user_id (int): Subject user identifier embedded in the token.

        Returns:
            AccessToken: Access token model.

        """
        expiration = datetime.now(timezone.utc) + timedelta(days=1)
        payload = JWTTokenMetadata(user_id=user_id, exp=expiration)
        token = jwt.encode(payload=payload.model_dump(), key=self.secret_key, algorithm=self.algorithm)
        return AccessToken(token=token, expires_at=expiration)

    def decode_token(self, token: str, verify_signature: bool = True) -> JWTTokenMetadata:
        """Parse a JWT and return structured metadata.

        Args:
            token (str): Compact serialized JWT.
            verify_signature (bool, optional): Whether to verify the signature.
                Defaults to True.

        Returns:
            JWTTokenMetadata: Decoded claims including user id and expiry.

        """
        options = Options(verify_signature=verify_signature, verify_exp=True)
        payload = jwt.decode(jwt=token, key=self.secret_key, algorithms=[self.algorithm], options=options)

        if "user_id" not in payload or "exp" not in payload:
            raise InvalidTokenError("Token is missing required claims")

        return JWTTokenMetadata(
            user_id=payload["user_id"],
            exp=datetime.fromtimestamp(payload["exp"], timezone.utc),
        )
