/**
 * Barrel module for the homePage: re-exports {@link HomePage}.
 *
 * @module pages/home/index
 */

import Container from '@mui/material/Container';
import { useState, useEffect } from 'react';

import { BooksShell } from '@components/booksShell';
import { useBookAPIClient, type SimpleBookType } from '@services/apiClient/book';

/**
 * Application landing route: loads up to five books via `getBooks(5)` (API default sorting and
 * pagination), then renders them through `BooksShell`; while the request runs, the shell shows
 * skeleton placeholders. Clearing state on unmount avoids carrying stale data into future visits.
 *
 * @returns {JSX.Element} Top-level Material UI `Container` wrapping the grid shell for that list.
 */
export function HomePage() {
  const [newestBooks, setNewestBooks] = useState<SimpleBookType[] | null>(null);

  const { getBooks } = useBookAPIClient();

  useEffect(() => {
    if (newestBooks === null) {
      getBooks(5).then(({ data }) => setNewestBooks(data));
    }

    return () => {
      setNewestBooks(null);
    };
  }, []);

  return (
    <Container>
      <BooksShell books={newestBooks} />
    </Container>
  );
}
