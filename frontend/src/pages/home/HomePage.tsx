/**
 * HomePage.tsx
 *
 * This file contains the HomePage component, which is the landing page of the application.
 * It loads up to five books via `getBooks(5)` (API default sorting and pagination), then renders them through `BooksShell`.
 *
 * @returns {JSX.Element} Top-level Material UI `Container` wrapping the grid shell for that list.
 */

import Chip from '@mui/material/Chip';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import { useState, useEffect } from 'react';

import { BooksShell } from '@components/booksShell';
import { useBookAPIClient, type BookType } from '@services/apiClient/book';

/**
 * Application landing route: loads up to five books via `getBooks(5)` (API default sorting and
 * pagination), then renders them through `BooksShell`; while the request runs, the shell shows
 * skeleton placeholders. Clearing state on unmount avoids carrying stale data into future visits.
 *
 * @returns {JSX.Element} Top-level Material UI `Container` wrapping the grid shell for that list.
 */
export function HomePage() {
  const [popularBooks, setPopularBooks] = useState<BookType[] | null>(null);
  const [newestBooks, setNewestBooks] = useState<BookType[] | null>(null);

  const { getBooks } = useBookAPIClient();

  useEffect(() => {
    if (newestBooks === null) {
      getBooks(5, 0, 'created_at', 'desc').then(({ data }) => setNewestBooks(data));
    }
    if (popularBooks === null) {
      getBooks(5, 0, 'watches_count', 'desc').then(({ data }) => setPopularBooks(data));
    }

    return () => {
      setNewestBooks(null);
    };
  }, []);

  return (
    <Container>
      <Divider sx={{ my: 2 }}>
        <Chip label="Popular Books" color="secondary" />
      </Divider>
      <BooksShell books={popularBooks} />
      <Divider sx={{ my: 2 }}>
        <Chip label="Newest Books" color="secondary" />
      </Divider>
      <BooksShell books={newestBooks} />
    </Container>
  );
}
