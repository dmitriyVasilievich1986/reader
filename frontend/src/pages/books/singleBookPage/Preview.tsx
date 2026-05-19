/**
 * Barrel module for the bookPreview: re-exports {@link BookPreview}.
 *
 * @module pages/books/singleBookPage/Preview
 */

import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Skeleton from '@mui/material/Skeleton';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';

import { usePageAPIClient, type PageType } from '@services/apiClient/page';

import styles from './style.module.css';

/**
 * Horizontal preview of up to four pages for the book in the route (`bookId` from `useParams`):
 * fetches rows ordered by ascending `position` with `book_id` equal to that id via `getPages`, then
 * renders cover thumbnails in a five-column `ImageList`. While loading—or when `bookId` is missing—shows
 * skeleton tiles; tapping a thumbnail opens `/book/:bookId/read?page=<position>`.
 *
 * @param {number} bookId - Book id.
 * @returns {JSX.Element} Skeleton grid when `pages` is `null`, otherwise the clickable preview strip.
 */
export function BookPreview({ bookId }: { bookId: number }) {
  const navigate = useNavigate();

  const [pages, setPages] = useState<PageType[] | null>(null);

  const { getPages } = usePageAPIClient();

  useEffect(() => {
    if (!bookId) return;

    getPages(4, 0, 'position', 'asc', [{ column: 'book_id', operator: 'eq', value: bookId }]).then(
      ({ data }) => setPages(data)
    );

    return () => {
      setPages(null);
    };
  }, [bookId]);

  if (pages === null)
    return (
      <ImageList className={styles.previewImageListLoading} cols={5} gap={4}>
        {Array.from({ length: 5 }).map((_, index) => (
          <ImageListItem key={index}>
            <Skeleton
              className={styles.previewSkeletonThumb}
              variant="rectangular"
              height="300px"
              width="200px"
            />
          </ImageListItem>
        ))}
      </ImageList>
    );
  return (
    <ImageList className={styles.previewImageList} cols={5} gap={4}>
      {pages.map((page) => (
        <ImageListItem
          key={page.id}
          className={styles.previewItem}
          onClick={() => navigate(`/book/${bookId}/read?page=${page.position}`)}
        >
          <img src={page.cover} alt={page.position.toString()} className={styles.previewThumb} />
        </ImageListItem>
      ))}
    </ImageList>
  );
}
