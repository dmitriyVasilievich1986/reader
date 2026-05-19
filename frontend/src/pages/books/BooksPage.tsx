/**
 * Barrel module for the booksPage: re-exports {@link BooksPage}.
 *
 * @module pages/books/index
 */

import Container from '@mui/material/Container';
import Pagination from '@mui/material/Pagination';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router';

import { BooksShell } from '@components/booksShell';
import { useBookAPIClient, type BookType } from '@services/apiClient/book';
import { parseIntWithCheck } from '@utils/parseIntWithCheck';

/**
 * Books list route: loads up to ten books via `getBooks(10)` (API sorting and pagination), then
 * renders them through `BooksShell`; while the request runs, the shell shows skeleton placeholders.
 * Clearing state on unmount avoids carrying stale data into future visits.
 *
 * @returns {JSX.Element} Top-level Material UI `Container` wrapping the grid shell for that list.
 */
export function BooksPage() {
  const limit = 10;

  const [searchParams, setSearchParams] = useSearchParams();

  const [books, setBooks] = useState<BookType[] | null>(null);
  const [totalBooks, setTotalBooks] = useState<number>(limit);
  const [page, setPage] = useState<number>(parseIntWithCheck(searchParams.get('page')));

  const { getBooks } = useBookAPIClient();

  useEffect(() => {
    const currentPage = parseIntWithCheck(searchParams.get('page'), { defaultValue: page });

    if (!searchParams.get('page')) {
      setSearchParams((prev) => {
        prev.set('page', currentPage.toString());
        return prev;
      });
    }

    if (books === null) {
      getBooks(limit, (currentPage - 1) * limit, 'created_at', 'desc').then(
        ({ data, metadata }) => {
          setBooks(data);
          setTotalBooks(metadata.total);
          setPage(Math.floor(metadata.offset / limit) + 1);
        }
      );
    }

    return () => {
      setBooks(null);
    };
  }, [searchParams]);

  return (
    <Container>
      <Pagination
        count={Math.ceil(totalBooks / limit)}
        page={page}
        color="primary"
        shape="circular"
        sx={{ mt: 2 }}
        onChange={(_, value) => {
          setBooks(null);
          setSearchParams((prev) => {
            prev.set('page', value.toString());
            return prev;
          });
        }}
      />
      <BooksShell books={books} />
    </Container>
  );
}
