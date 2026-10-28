"""Async Click CLI command that syncs a library folder of authors and books into the database."""

__all__ = ("sync_books",)

from pathlib import Path

import asyncclick as click

from reader.commands.sync_books import SyncBooksCommand
from reader.config import AppConfig


@click.command(help="Sync a library folder of authors and books into the database.")
@click.option(
    "--library-path",
    type=click.Path(path_type=Path),
    required=True,
    help="Library folder with one <first>_<last> sub-folder per author.",
)
@click.option("--static-url", type=str, default="/static/images", help="The URL prefix for page images.")
@click.option("--preview", is_flag=True, default=False, help="Print what would be added without saving it.")
@click.pass_context
async def sync_books(ctx: click.Context, library_path: Path, static_url: str, preview: bool) -> None:
    """Validate the library, print what will be added and save it unless ``preview`` is set.

    Args:
        ctx (click.Context): Command context with ``config`` in ``ctx.obj``.
        library_path (Path): Library folder with one sub-folder per author.
        static_url (str, optional): URL prefix for page images. Defaults to ``/static/images``.
        preview (bool, optional): If true, only print the parsed library. Defaults to ``False``.

    Returns:
        None

    Raises:
        click.ClickException: If the library fails validation.

    """
    app_config: AppConfig = ctx.obj["config"]
    command = SyncBooksCommand(library_path=library_path, static_url=static_url, app_config=app_config)
    await command.initialize()
    try:
        await command.validate()
    except ValueError as e:
        raise click.ClickException(str(e)) from e

    click.echo(str(command))
    if preview:
        return

    await command.execute()
    click.echo("Library synced successfully.")
