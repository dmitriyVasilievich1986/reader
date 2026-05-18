"""Async Click CLI subcommands for user administration."""

__all__ = ("user",)

import asyncclick as click

from reader.config.app_config import AppConfig
from reader.modules.routers.models.responses.user import GetSingleUserResponse
from reader.services.auth import PasswordService
from reader.services.daos.user_dao import UserDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models.user import User


@click.group(help="CLI for managing users.")
@click.pass_context
def user(ctx: click.Context) -> None:
    """Attach a database client for nested user commands.

    Args:
        ctx (click.Context): Parent command context with ``config`` in ``ctx.obj``.

    Returns:
        None

    """
    app_config: AppConfig = ctx.obj["config"]
    ctx.obj["db"] = AsyncDatabaseClient(app_config=app_config)


@user.command(help="Create a new user.")
@click.option("--username", type=str, required=True, help="The username of the user.")
@click.option("--email", type=str, required=True, help="The email of the user.")
@click.option("--is-admin", is_flag=True, default=False, help="Whether the user is an admin.")
@click.option("--password", type=str, required=True, help="The password of the user.", hide_input=True, prompt=True)
@click.option("--first-name", type=str, required=False, help="The first name of the user.")
@click.option("--last-name", type=str, required=False, help="The last name of the user.")
@click.option("--photo-url", type=str, required=False, help="The photo URL of the user.")
@click.pass_context
async def create_user(
    ctx: click.Context,
    username: str,
    email: str,
    is_admin: bool,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
    photo_url: str | None = None,
) -> None:
    """Persist a user and echo the payload matching ``GetSingleUserResponse``.

    Args:
        ctx (click.Context): Command context with ``db`` attached by ``user``.
        username (str): Unique username for the new account.
        email (str): Email address for the new account.
        is_admin (bool, optional): Grant administrator privileges. Defaults to ``False``.
        password (str): Plaintext password to hash and store.
        first_name (str, optional): Optional given name.
        last_name (str, optional): Optional family name.
        photo_url (str, optional): Optional profile image URL.

    Returns:
        None

    """
    db: AsyncDatabaseClient = ctx.obj["db"]
    user_dao: UserDAO = UserDAO(database_client=db)
    user: User = await user_dao.create(
        username=username,
        email=email,
        is_admin=is_admin,
        password=password,
        first_name=first_name,
        last_name=last_name,
        photo_url=photo_url,
    )
    payload = GetSingleUserResponse.model_validate(user)

    click.echo(f"User created successfully:\n{payload.model_dump_json(indent=2)}")


@user.command(help="Check password")
@click.option("--password", type=str, required=True, help="The password of the user.", hide_input=True, prompt=True)
@click.option("--username", type=str, required=True, help="The username to check.")
@click.pass_context
async def check_password(ctx: click.Context, password: str, username: str) -> None:
    """Compare a candidate password with the stored hash for ``username``.

    Args:
        ctx (click.Context): Command context with ``db`` attached by ``user``.
        password (str): Plaintext password to verify.
        username (str): Existing user's username.

    Returns:
        None

    """
    db: AsyncDatabaseClient = ctx.obj["db"]
    user_dao: UserDAO = UserDAO(database_client=db)
    user: User = await user_dao.get_by_username(username)

    if not PasswordService.check_password(password, user.password):
        click.echo("Password is incorrect.")
    else:
        click.echo("Password is correct.")
