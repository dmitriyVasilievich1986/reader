"""Flask CLI commands for the Reader application."""

__all__ = ("main",)

import re
from pathlib import Path

import click
import pydash
from flask.cli import FlaskGroup

from reader import db
from reader.app import create_app
from reader.models.main import Author, Book, Page

main = FlaskGroup(create_app=create_app)


@main.command(help="Add a new book from a folder containing its pages")
@click.option("--path", "-P", type=click.Path(exists=True), help="Path to the folder containing book pages")
def add_book(path: str) -> None:
    """Create an author if needed and persist a book with page metadata from disk.

    The book title is the basename of ``path``; the parent directory name is
    treated as ``{first}-{last}`` for the author. Static URLs are derived from
    those names and each page filename.

    Args:
        path (str): Filesystem path to the directory holding the book page
            files.

    Returns:
        None.

    Raises:
        click.ClickException: If ``path`` contains no files, or if a book with
            the same name and author already exists.

    """
    folder_path = Path(path)
    name = folder_path.name
    author_name = folder_path.parent.name
    name_splited = author_name.split("-")
    first_name = pydash.get(name_splited, "0", "")
    last_name = pydash.get(name_splited, "1", "")
    author = db.session.query(Author).filter(Author.first_name == first_name).first()
    if author is None:
        author = Author(first_name=first_name, last_name=last_name)
        db.session.add(author)
        db.session.commit()
    pages = sorted(folder_path.iterdir())
    if len(pages) == 0:
        raise click.ClickException(f"No pages found in the folder: {path}")
    book = db.session.query(Book).filter(Book.name == name, Book.author_id == author.id).first()
    if book is not None:
        raise click.ClickException(f"Book '{name}' by '{author_name}' already exists.")
    cover_url = f"/static/i/{author_name}/{name}/{pydash.get(pages, '0.name', '')}"
    book = Book(author=author, name=name, cover=cover_url)
    click.echo(f"Adding book '{book.name}' by '{author.first_name}' from path: {path}")
    db.session.add(book)
    db.session.commit()
    for _, f in enumerate(pages, start=1):
        url = f"/static/i/{author_name}/{name}/{f.name}"
        position = int(re.search(r"(\d+)", f.name).group(0))
        page = Page(book=book, position=position, cover=url)
        db.session.add(page)
        click.echo(f"\tAdding page {position}: {url}")
    db.session.commit()
