"""Async Click CLI for configuring and running the Reader application."""

__all__ = ("main",)

import asyncclick as click
import uvicorn

from reader import __version__ as app_version
from reader.config import AppConfig

from .sync_books import sync_books
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
@click.pass_context
def run(ctx: click.Context, host: str, port: int) -> None:
    """Start uvicorn serving the Reader ASGI application.

    Args:
        ctx (click.Context): Command context populated by ``main``.
        host (str): Bind address for the HTTP server.
        port (int): TCP port for the HTTP server.

    Returns:
        None

    """
    config: AppConfig = ctx.obj["config"]
    click.echo(f"Starting Reader on {host}:{port}")
    uvicorn.run(
        "reader.modules.app:get_app",
        host=host,
        port=port,
        reload=True,
        factory=True,
        log_level=config.info.api_info.log_level.lower(),
    )


main.add_command(sync_books)
main.add_command(user)
