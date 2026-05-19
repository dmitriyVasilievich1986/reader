/**
 * BooksShell.tsx
 *
 * This file contains the BooksShell component, which is a responsive five-column shell for browsing books.
 * It shows skeleton placeholders when the books are not loaded, otherwise it shows the books as a grid of covers with a title/action bar revealed on hover or keyboard focus (`focus-within`).
 * Selecting a tile navigates to `/book/:bookId`.
 *
 * @param {object} props - Component props.
 * @param {SimpleBookType[] | null} props.books - Library rows to render, or `null` while loading.
 * @returns {JSX.Element} Skeleton grid without `Container`, or book grid wrapped in Material UI `Container`.
 */

import InfoIcon from '@mui/icons-material/Info';
import Container from '@mui/material/Container';
import IconButton from '@mui/material/IconButton';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import ImageListItemBar from '@mui/material/ImageListItemBar';
import Skeleton from '@mui/material/Skeleton';
import { getAuthorName } from '@utils';
import { useNavigate } from 'react-router';

import type { BookType } from '@services/apiClient/book';

import styles from './style.module.css';

/**
 * Responsive five-column shell for browsing books: skeleton placeholders when `props.books` is `null`,
 * otherwise covers with a title/action bar revealed on hover or keyboard focus (`focus-within`).
 * Selecting a tile navigates to `/book/:bookId`.
 *
 * @param {object} props - Component props.
 * @param {BookType[] | null} props.books - Library rows to render, or `null` while loading.
 * @returns {JSX.Element} Skeleton grid without `Container`, or book grid wrapped in Material UI `Container`.
 */
export function BooksShell({ books }: { books: BookType[] | null }) {
  const navigate = useNavigate();

  if (books === null)
    return (
      <ImageList className={styles.bookList} cols={5} gap={4}>
        {Array.from({ length: 5 }).map((_, index) => (
          <ImageListItem key={index}>
            <Skeleton width={200} height={300} variant="rectangular" />
          </ImageListItem>
        ))}
      </ImageList>
    );

  return (
    <Container>
      <ImageList className={styles.bookList} cols={5} gap={4}>
        {books.map((book) => (
          <ImageListItem
            key={book.id}
            className={styles.listItem}
            onClick={() => navigate(`/book/${book.slug}`)}
          >
            <img src={book.cover} alt={book.name} className={styles.bookCover} />
            <ImageListItemBar
              className={styles.itemBar}
              title={book.name}
              subtitle={`By ${getAuthorName(book.author)}`}
              actionIcon={
                <IconButton
                  className={styles.infoIconButton}
                  aria-label={`info about ${book.name}`}
                >
                  <InfoIcon />
                </IconButton>
              }
            />
          </ImageListItem>
        ))}
      </ImageList>
    </Container>
  );
}
