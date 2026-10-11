/**
 * Barrel module for the singleBookPage: re-exports {@link SingleBookPage}.
 *
 * @module pages/books/singleBookPage/SingleBookPage
 */

import VisibilityIcon from '@mui/icons-material/Visibility';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';
import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router';

import { Image } from '@components/image/Image';
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

  const { getBookBySlug, incrementWatchesCount } = useBookAPIClient();

  useEffect(() => {
    if (!bookId) return;

    getBookBySlug(bookId).then(setBook);

    return () => {
      setBook(null);
    };
  }, [bookId]);

  const readBookClickHandler = () => {
    if (!book) return;

    void incrementWatchesCount(book.id).catch((error) => {
      console.error('Failed to increment watches count', error);
    });
    navigate(`/book/${book.id}/read`);
  };

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
          <Image src={book.cover} alt={book.name} className={styles.cover} />
          <Box>
            <Typography className={styles.title} variant="h4">
              {book.name}
            </Typography>
            <Typography className={styles.author} variant="body1">
              {authorName}
            </Typography>
            <Box className={styles.watchesCountContainer}>
              <VisibilityIcon />
              <Typography className={styles.watchesCount} variant="body1">
                {book.watchesCount} views
              </Typography>
            </Box>
            <Button
              className={styles.readButton}
              variant="contained"
              onClick={readBookClickHandler}
            >
              Read
            </Button>
          </Box>
        </Box>
      </Box>
      <BookPreview bookId={book.id} />
    </Container>
  );
}
