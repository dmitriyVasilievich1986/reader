/**
 * Barrel module for the booksPage: re-exports {@link BooksPage}.
 *
 * @module pages/books/index
 */

import Container from '@mui/material/Container';
import { useState, useEffect } from 'react';

import { BooksShell } from '@components/booksShell';
import { useBookAPIClient, type SimpleBookType } from '@services/apiClient/book';

/**
 * Books list route: loads up to ten books via `getBooks(10)` (API sorting and pagination), then
 * renders them through `BooksShell`; while the request runs, the shell shows skeleton placeholders.
 * Clearing state on unmount avoids carrying stale data into future visits.
 *
 * @returns {JSX.Element} Top-level Material UI `Container` wrapping the grid shell for that list.
 */
export function BooksPage() {
  const [books, setBooks] = useState<SimpleBookType[] | null>(null);

  const { getBooks } = useBookAPIClient();

  useEffect(() => {
    if (books === null) {
      getBooks(10).then(({ data }) => setBooks(data));
    }

    return () => {
      setBooks(null);
    };
  }, []);

  return (
    <Container>
      <BooksShell books={books} />
    </Container>
  );
}
