/**
 * Barrel module for the singleBookPage: re-exports {@link SingleBookPage}.
 *
 * @module pages/books/singleBookPage/SingleBookPage
 */

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';
import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router';

import { useBookAPIClient, type BookType } from '@services/apiClient/book';

import { BookPreview } from './Preview';
import styles from './style.module.css';

/**
 * Single book page route: fetches the book by `bookId` from `useParams`, then renders it through
 * `BookPreview` (which loads up to four pages for preview). While loading—or when `bookId` is missing—shows
 * a skeleton for the hero section; tapping the read button navigates to `/book/:bookId/read`.
 *
 * @returns {JSX.Element} Skeleton container when `book` is `null`, otherwise the book page layout.
 */
export function SingleBookPage() {
  const { bookId } = useParams();
  const navigate = useNavigate();

  const [book, setBook] = useState<BookType | null>(null);

  const { getBook } = useBookAPIClient();

  useEffect(() => {
    if (!bookId) return;

    getBook(parseInt(bookId)).then(setBook);

    return () => {
      setBook(null);
    };
  }, [bookId]);

  const authorName = useMemo(() => {
    if (!book) return '';
    if (book.author.lastName === null) {
      return book.author.firstName;
    }
    return `${book.author.firstName} ${book.author.lastName}`;
  }, [book]);

  if (book === null)
    return (
      <Container>
        <Skeleton
          className={styles.loadingSkeleton}
          variant="rectangular"
          height="300px"
          width="100%"
        />
      </Container>
    );

  return (
    <Container>
      <Box className={styles.hero}>
        <Box className={styles.heroInner}>
          <img src={book.cover} alt={book.name} className={styles.cover} />
          <Box>
            <Typography className={styles.title} variant="h4">
              {book.name}
            </Typography>
            <Typography className={styles.author} variant="body1">
              {authorName}
            </Typography>
            <Button
              className={styles.readButton}
              variant="contained"
              onClick={() => navigate(`/book/${bookId}/read`)}
            >
              Read
            </Button>
          </Box>
        </Box>
      </Box>
      <BookPreview />
    </Container>
  );
}
