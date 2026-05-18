"""HTTP API routes for user login and the current account."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from reader.config.app_config import AppConfig
from reader.modules.middlewares.dependencies import get_config, get_db
from reader.modules.middlewares.dependencies.user_authorized import user_authorized
from reader.modules.routers.models.requests.user import LoginBody, PatchUserBody
from reader.modules.routers.models.responses.user import GetSingleUserResponse, LoginResponse
from reader.services.auth import JWTTokenService, PasswordService
from reader.services.daos.user_dao import UserDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models.user import User

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK, summary="Login a user")
async def login(
    body: Annotated[LoginBody, Body(..., description="The body of the login")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    config: Annotated[AppConfig, Depends(get_config)],
) -> LoginResponse:
    """Authenticate a user and return a JWT.

    Args:
        body (LoginBody): Username and password submitted by the client.
        db (AsyncDatabaseClient): Database client from dependency injection.
        config (AppConfig): Application configuration from dependency injection.

    Returns:
        LoginResponse: Signed access token and its expiry time.

    Raises:
        HTTPException: If credentials are wrong (401) or loading the user fails
            (500).

    """
    user_dao = UserDAO(database_client=db)

    try:
        payload = await user_dao.get_by_username(body.username)
    except NoResultFound as e:
        logger.error(f"User with username {body.username} not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting user", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting user") from e

    if not PasswordService.check_password(body.password, payload.password):
        logger.error(f"Invalid password for user {body.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    jwt_service = JWTTokenService(
        secret_key=config.services.auth.jwt_secret_key.get_secret_value(), algorithm=config.services.auth.jwt_algorithm
    )
    access_token = jwt_service.generate_token(payload.id)

    return LoginResponse(access_token=access_token.token, expires_at=access_token.expires_at)


@router.get("/me", response_model=GetSingleUserResponse, status_code=status.HTTP_200_OK, summary="Get the current user")
async def get_current_user(
    user: Annotated[User, Depends(user_authorized)],
) -> GetSingleUserResponse:
    """Return the authenticated user resolved from the JWT.

    Args:
        user (User): Authenticated user model from dependency injection.

    Returns:
        GetSingleUserResponse: Public fields for the current user.

    """
    return GetSingleUserResponse.model_validate(user)


@router.patch(
    "/me", response_model=GetSingleUserResponse, status_code=status.HTTP_200_OK, summary="Patch the current user"
)
async def patch_current_user(
    body: Annotated[PatchUserBody, Body(..., description="The body of the patch")],
    user: Annotated[User, Depends(user_authorized)],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleUserResponse:
    """Apply partial updates to the authenticated user profile.

    Args:
        body (PatchUserBody): Fields to change; unset keys are not modified.
        user (User): Authenticated user model from dependency injection.
        db (AsyncDatabaseClient): Database client from dependency injection.

    Returns:
        GetSingleUserResponse: Updated public fields for the current user.

    Raises:
        HTTPException: If persisting the update fails (500).

    """
    user_dao = UserDAO(database_client=db)

    try:
        payload = await user_dao.update(user.id, **body.model_dump(exclude_unset=True))
    except SQLAlchemyError as e:
        logger.exception("Error patching user", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error patching user") from e

    return GetSingleUserResponse.model_validate(payload)
