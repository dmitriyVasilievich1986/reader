# sync_books

Commands that import a folder-based library of authors, books and page images
into the Reader database. There are three commands, nested from the library
level down to a single book:

| Command            | Input                 | Creates / reuses                                   |
| ------------------ | --------------------- | -------------------------------------------------- |
| `SyncBooksCommand` | library folder        | one `AddAuthorCommand` per author folder           |
| `AddAuthorCommand` | author folder         | an `Author` (existing one is reused) + its books   |
| `AddBookCommand`   | book folder + author  | one `Book` and one `Page` per image                |

All three implement the [`BaseCommand`](../base.py) interface and follow the
standard `initialize → validate → execute` lifecycle.

## Folder layout

```
<library>/                     # SyncBooksCommand(library_path=...)
└── <first>_<last>/            # AddAuthorCommand(author_path=...)
    └── <book_name>/           # AddBookCommand(book_path=..., author=...)
        ├── page_001.jpg
        ├── page_002.jpg
        └── ...
```

### Author folder

- The folder name is split on the **first** `_` into first and last name, and
  each part is capitalized: `lewis_carroll` → `Lewis` / `Carroll`.
- If an author with the same first and last name already exists, it is reused;
  otherwise a new `Author` is created.
- More than one matching author is a validation error.

### Book folder

- The book name is the folder name with `_` replaced by spaces, then
  capitalized: `alice_in_wonderland` → `Alice in wonderland`.
- A book with the same name must not already exist in the database.

### Page images

- Accepted extensions (case-insensitive): `.jpg`, `.jpeg`, `.png`, `.webp`.
  Other entries in the book folder are logged and skipped.
- The first number in the file name is the page position
  (`page_007.jpg` → `007`). An image without a number is a validation error.
- Pages are sorted by position, and the first page becomes the book cover.
- Each page's `cover` URL is
  `<static_url>/<author_folder>/<book_folder>/<file_name>`, where `static_url`
  defaults to `/static/images` (a trailing `/` is stripped).

## Lifecycle

1. `initialize(**kwargs)` — no-op on every command, kept for `BaseCommand`
   compatibility.
2. `validate()` — checks the folders and builds the ORM objects in memory
   without writing anything:
   - `SyncBooksCommand` builds and validates an `AddAuthorCommand` per entry in
     the library folder and stores them in `authors`.
   - `AddAuthorCommand` resolves `author` and builds and validates an
     `AddBookCommand` per entry in the author folder, storing them in `books`.
   - `AddBookCommand` builds `book` and the sorted `pages`.

   A child that fails validation is logged as a warning and skipped. A parent
   raises `ValueError` only when **none** of its children are valid.
3. `execute()` — saves everything to the database. Each command uses the
   `session` passed to its constructor, or opens its own session when none was
   given, and commits after saving its rows.

`str(command)` returns a plain-text tree of what will be saved, so you can call
it after `validate()` as a dry-run preview.

## Constructor arguments

| Argument       | Commands          | Default            | Description                                       |
| -------------- | ----------------- | ------------------ | ------------------------------------------------- |
| `library_path` | `SyncBooks`       | —                  | Root folder with one sub-folder per author.       |
| `author_path`  | `AddAuthor`       | —                  | Author folder named `<first>_<last>`.             |
| `book_path`    | `AddBook`         | —                  | Book folder with the page images.                 |
| `author`       | `AddBook`         | —                  | `Author` ORM object the book belongs to.          |
| `static_url`   | all               | `"/static/images"` | URL prefix for page images.                       |
| `session`      | all               | `None`             | `AsyncSession` to reuse instead of opening one.   |
| `app_config`   | all               | `None`             | `AppConfig`; the global singleton when omitted.   |

## Usage

### Sync a whole library

```python
from reader.commands.sync_books import SyncBooksCommand
from reader.config import AppConfig

command = SyncBooksCommand(
    library_path="/data/books",
    app_config=AppConfig.get_or_create(),
)

await command.initialize()
await command.validate()
print(command)  # dry-run preview
await command.execute()
```

### Add a single author

```python
from reader.commands.sync_books import AddAuthorCommand

command = AddAuthorCommand(author_path="/data/books/lewis_carroll")
await command.initialize()
await command.validate()
await command.execute()
```

### Preview output

```
Author:
	Name: Lewis Carroll
Book:
	Name: Alice in wonderland
	Pages:
		[001] - /static/images/lewis_carroll/alice_in_wonderland/page_001.jpg
		[002] - /static/images/lewis_carroll/alice_in_wonderland/page_002.jpg
```

## Errors

`validate()` raises `ValueError` when:

- **`SyncBooksCommand`** — the library path is missing or not a directory, or
  no author folder is valid.
- **`AddAuthorCommand`** — the author path is missing or not a directory, more
  than one author matches the name, or no book folder is valid.
- **`AddBookCommand`** — the book path is missing or not a directory, a book
  with the same name already exists, an image has no number in its name, or
  the folder has no page images.

`str(command)` raises `ValueError` if `validate()` has not completed
successfully.

## CLI

`SyncBooksCommand` is exposed as `reader sync-books`
(see [`utils/cli/sync_books.py`](../../utils/cli/sync_books.py)). It validates
the library, prints the preview, then saves everything:

```bash
# Import the whole library into the database
uv run --env-file=.env reader sync-books --library-path /data/books

# Print what would be added without saving anything
uv run --env-file=.env reader sync-books --library-path /data/books --preview

# Use a different URL prefix for page images
uv run --env-file=.env reader sync-books --library-path /data/books --static-url /media
```

Validation errors are reported as a CLI error with a non-zero exit code.
