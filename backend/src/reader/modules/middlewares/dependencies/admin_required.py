"""FastAPI dependency that gates routes behind an admin-only check."""

from typing import Annotated, TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from loguru import logger

from .user_authorized import user_authorized

if TYPE_CHECKING:
    from reader.services.database.models.user import User


async def admin_required(user: Annotated["User", Depends(user_authorized)]) -> "User":
    """Return the authenticated user only when they have admin privileges.

    Args:
        user (User): Authenticated user from ``user_authorized``.

    Returns:
        User: The same database row when ``user.is_admin`` is true.

    Raises:
        HTTPException: 403 if the user is not an admin.

    """
    if not user.is_admin:
        logger.warning("User is not an admin")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to access this resource"
        )

    return user
