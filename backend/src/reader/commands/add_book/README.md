# AddBookCommand

`AddBookCommand` imports a book from a local filesystem folder into the Reader
database. It scans a directory of page images, derives author and book metadata
from the folder layout, and persists author, book, and page rows in a single
transaction.

The command implements the [`BaseCommand`](../base.py) interface and follows the
standard `initialize → validate → execute` lifecycle.

## Folder layout

The command expects a two-level directory layout:

```
<authors_root>/
└── <first>_<last>/        # parent folder — encodes the author name
    └── <book name>/       # book folder — passed as `book_path`
        ├── 001.jpg
        ├── 002.jpg
        └── ...
```

Rules applied during `validate()`:

- `book_path` must exist and be a directory.
- `book_path` must contain at least one `.jpg`, `.jpeg`, or `.png` file.
- The parent folder name is split on `_` to derive the author:
  - `first_last` → `author_first_name = "first"`, `author_last_name = "last"`.
  - `first` → `author_first_name = "first"` (no last name).
  - More than two `_`-separated segments → `ValueError`.
- `book_name` is derived from the book folder name by replacing `_` and
  whitespace with single spaces and capitalising the first character
  (e.g. `the_little_prince` → `The little prince`).

Page records are stored with URLs of the form
`/static/i/<authors_root>/<author_folder>/<filename>`, sorted lexicographically.
The first page is also used as the book cover.

## Public attributes

| Attribute           | Type                | Populated by | Description                                  |
| ------------------- | ------------------- | ------------ | -------------------------------------------- |
| `book_path`         | `Path`              | `__init__`   | Directory holding the page images.           |
| `app_config`        | `AppConfig`         | `__init__`   | Database/app configuration.                  |
| `author_first_name` | `str \| None`       | `validate`   | Parsed from the parent folder name.          |
| `author_last_name`  | `str \| None`       | `validate`   | Parsed from the parent folder name.          |
| `book_name`         | `str \| None`       | `validate`   | Derived from `book_path.name`.               |
| `author_full_name`  | `str` (property)    | computed     | `"first"` or `"first last"`.                 |

## Lifecycle

1. `initialize(**kwargs)` — no-op, kept for `BaseCommand` compatibility.
2. `validate()` — checks the folder layout and populates `book_name`,
   `author_first_name`, and `author_last_name`. Raises `ValueError` on any
   layout violation.
3. `execute()` — opens a database session and creates one `Author`, one `Book`,
   and one `Page` per image. Logs a JSON summary of what was inserted.

`str(command)` returns a JSON snapshot of the current command state, which is
useful for dry-run previews before calling `execute()`.

## Usage examples

### Programmatic use

```python
from pathlib import Path

from reader.commands.add_book import AddBookCommand
from reader.config import AppConfig

command = AddBookCommand(
    book_path=Path("/data/books/antoine_de-saint-exupery/the_little_prince"),
    app_config=AppConfig.get_or_create(),
)

await command.initialize()
await command.validate()
await command.execute()
```

### Dry-run preview

`__str__` returns the parsed metadata without touching the database:

```python
command = AddBookCommand("/data/books/lewis_carroll/alice_in_wonderland")
await command.initialize()
await command.validate()
print(command)
```

Example output:

```json
{
  "Book path": "/data/books/lewis_carroll/alice_in_wonderland",
  "Author first name": "lewis",
  "Author last name": "carroll",
  "Author full name": "lewis carroll",
  "Book name": "Alice in wonderland"
}
```

### CLI

The command is wired into the Reader CLI as `add-book`
(see [`utils/cli/main.py`](../../utils/cli/main.py)):

```bash
# Import the book into the database
reader add-book --book-path /data/books/lewis_carroll/alice_in_wonderland

# Print the parsed structure without persisting anything
reader add-book --book-path /data/books/lewis_carroll/alice_in_wonderland --preview
```

## Errors

`validate()` raises `ValueError` when:

- `book_path` does not exist or is not a directory.
- The parent of `book_path` is not a directory.
- `book_path` contains no `.jpg`/`.jpeg`/`.png` files.
- The parent folder name has more than two `_`-separated segments.
