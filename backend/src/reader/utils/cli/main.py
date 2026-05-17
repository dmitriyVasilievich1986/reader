"""Async Click CLI for configuring and running the Reader application."""

__all__ = ("main",)

import asyncclick as click
import uvicorn

from reader import __version__ as app_version
from reader.config import AppConfig


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
