"""FastAPI dependencies for JWT Bearer authentication.

``user_token`` wires the OpenAPI security scheme; ``user_authorized`` decodes
the JWT, loads the matching ``User`` from the database, or raises ``HTTPException``.
"""

__all__ = ("user_authorized",)

from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from reader.config.app_config import AppConfig
from reader.services.auth import JWTTokenService
from reader.services.daos import UserDAO
from reader.services.database import AsyncDatabaseClient

if TYPE_CHECKING:
    from reader.services.database.models.user import User

from .get_db import get_db

user_token = HTTPBearer(scheme_name="User Token", auto_error=False)


async def user_authorized(
    token_header: Annotated[HTTPAuthorizationCredentials | None, Depends(user_token)],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> "User":
    """Decode the Bearer JWT and return the authenticated user row.

    Args:
        token_header (HTTPAuthorizationCredentials): Parsed ``Authorization``
            Bearer credentials from the request.
        db (AsyncDatabaseClient): Client used to load the user by primary key.

    Returns:
        User: Database row for the ``user_id`` embedded in the token.

    Raises:
        HTTPException: 401 if the token is expired, malformed, or the user is
            missing; 500 if loading the user fails with a database error.

    """
    if token_header is None:
        logger.error("No token provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    user_dao = UserDAO(database_client=db)
    jwt_token_service = JWTTokenService(
        secret_key=AppConfig.get_or_create().services.auth.jwt_secret_key.get_secret_value(),
        algorithm=AppConfig.get_or_create().services.auth.jwt_algorithm,
    )
    try:
        jwt_token_metadata = jwt_token_service.decode_token(token_header.credentials)
    except ExpiredSignatureError as e:
        logger.warning("Token expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from e
    except PyJWTError as e:
        logger.exception("Invalid token", exc_info=e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e

    try:
        return await user_dao.get_by_pk(jwt_token_metadata.user_id)
    except NoResultFound as e:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found") from e
    except SQLAlchemyError as e:
        logger.exception("Something went wrong while retrieving the user", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while retrieving the user"
        ) from e
