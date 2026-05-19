"""Async Click CLI for configuring and running the Reader application."""

__all__ = ("main",)

import asyncclick as click
import uvicorn

from reader import __version__ as app_version
from reader.commands.add_book import AddBookCommand
from reader.config import AppConfig

from .user import user


@click.group(help="CLI for managing the Reader.")
@click.version_option(app_version, "-v", "--version", message=f"Reader, version {app_version}")
@click.pass_context
async def main(ctx: click.Context) -> None:
    """Root command group that loads shared application configuration.

    Args:
        ctx (click.Context): Click invocation context holding per-command state.

    Returns:
        None

    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = AppConfig.get_or_create()


@main.command(help="Show the Reader application configuration.")
@click.pass_context
async def show_config(ctx: click.Context) -> None:
    """Print the resolved application configuration as formatted JSON.

    Args:
        ctx (click.Context): Command context populated by ``main``.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    click.echo(config.model_dump_json(indent=2))


@main.command(help="Start the Reader application server.")
@click.option("--host", default="0.0.0.0", help="Host to bind the server to.")
@click.option("--port", default=8000, help="Port to bind the server to.")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development.")
def run(host: str, port: int, reload: bool) -> None:
    """Start uvicorn serving the Reader ASGI application.

    Args:
        host (str): Bind address for the HTTP server.
        port (int): TCP port for the HTTP server.
        reload (bool, optional): Enable dev auto-reload. Defaults to ``False``.

    Returns:
        None

    """
    click.echo(f"Starting Reader on {host}:{port} (reload={reload})")
    uvicorn.run(
        "reader.modules.app:get_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@main.command(help="Add a book to the Reader application.")
@click.option("--book-path", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True)
@click.option("--preview", is_flag=True, help="Preview the book structure.", default=False)
@click.option("--static-url", type=str, help="The URL prefix for static files.", default="/static/images")
@click.pass_context
async def add_book(ctx: click.Context, book_path: str, preview: bool, static_url: str) -> None:
    """Add a book from a local directory or print a dry-run preview.

    Initializes and validates the add-book workflow against ``book_path``. When
    ``preview`` is set, prints the command state without persisting changes.

    Args:
        ctx (click.Context): Command context populated by ``main``.
        book_path (str): Path to the book directory on disk.
        preview (bool, optional): If true, print the command only. Defaults to
            ``False``.
        static_url (str, optional): The URL prefix for static files.
            Defaults to ``/static/images``.

    Returns:
        None

    """
    app_config: AppConfig = ctx.obj["config"]
    command = AddBookCommand(book_path, app_config=app_config, static_url=static_url)
    await command.initialize()
    await command.validate()

    if preview:
        click.echo(str(command))
    else:
        await command.execute()


main.add_command(user)
