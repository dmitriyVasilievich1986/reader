/**
 * ReadBookPage.tsx
 *
 * This file contains the ReadBookPage component, which is the page that displays the book reader.
 * It fetches the pages for the book from the API and displays them in a scrollable container.
 *
 * @returns {JSX.Element} The ReadBookPage component.
 */

import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Container from '@mui/material/Container';
import Fade from '@mui/material/Fade';
import LinearProgress from '@mui/material/LinearProgress';
import Stack from '@mui/material/Stack';
import { useEffect, useRef, useState } from 'react';
import { useParams, useSearchParams } from 'react-router';

import { usePageAPIClient, type PageType } from '@services/apiClient/page';

import styles from './style.module.css';

/**
 * Single book reader page route: fetches the pages for the book by `bookId` from `useParams`, then renders them in a scrollable container.
 * While loading—or when `bookId` is missing—shows a skeleton for the hero section; tapping the read button navigates to `/book/:bookId/read`.
 *
 * @returns {JSX.Element} Skeleton container when `pages` is `null`, otherwise the book reader page layout.
 */
export function ReadBookPage() {
  const { bookId } = useParams();

  const [searchParams, setSearchParams] = useSearchParams();

  const { getPages } = usePageAPIClient();

  const [isScrolling, setIsScrolling] = useState(false);
  const [pages, setPages] = useState<PageType[]>([]);
  const [currentPosition, setCurrentPosition] = useState<number>(
    searchParams.get('page') ? Number(searchParams.get('page')) : 1
  );

  const imageRefs = useRef<Map<number, HTMLImageElement>>(new Map());
  const didInitialScroll = useRef(false);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    const onScroll = () => {
      setIsScrolling(true);
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => setIsScrolling(false), 1000);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      clearTimeout(timeoutId);
    };
  }, []);

  useEffect(() => {
    if (!bookId) return;

    getPages(100, 0, 'position', 'asc', [
      { column: 'book_id', operator: 'eq', value: parseInt(bookId) },
    ]).then(({ data }) => setPages(data));
  }, [bookId]);

  useEffect(() => {
    if (pages.length === 0) return;

    let cancelled = false;
    let observer: IntersectionObserver | null = null;

    const attachObserver = () => {
      if (cancelled) return;
      observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            const position = Number((entry.target as HTMLElement).dataset.position);
            setCurrentPosition(position);
            setSearchParams(
              (prev) => {
                prev.set('page', position.toString());
                return prev;
              },
              { replace: true }
            );
          }
        },
        { rootMargin: '-50% 0px -50% 0px' }
      );
      imageRefs.current.forEach((img) => observer!.observe(img));
    };

    const waitForImage = (img?: HTMLImageElement) =>
      new Promise<void>((resolve) => {
        if (!img || (img.complete && img.naturalHeight > 0)) {
          resolve();
          return;
        }
        const done = () => {
          img.removeEventListener('load', done);
          img.removeEventListener('error', done);
          resolve();
        };
        img.addEventListener('load', done);
        img.addEventListener('error', done);
      });

    if (didInitialScroll.current) {
      attachObserver();
    } else {
      const initial = searchParams.get('page');
      const targetPos = initial ? Number(initial) : null;
      const targetIndex =
        targetPos !== null ? pages.findIndex((p) => p.position === targetPos) : -1;

      if (targetIndex === -1) {
        didInitialScroll.current = true;
        attachObserver();
      } else {
        Promise.all(
          pages
            .slice(0, targetIndex + 1)
            .map((p) => waitForImage(imageRefs.current.get(p.position)))
        ).then(() => {
          if (cancelled) return;
          imageRefs.current
            .get(targetPos!)
            ?.scrollIntoView({ behavior: 'instant', block: 'start' });
          didInitialScroll.current = true;
          attachObserver();
        });
      }
    }

    return () => {
      cancelled = true;
      observer?.disconnect();
    };
  }, [pages, setSearchParams]);

  const progress = pages.length > 0 ? (currentPosition / pages.length) * 100 : 0;

  return (
    <Container>
      <Box className={styles.stickyProgressWrap}>
        <LinearProgress variant="determinate" value={progress} />
      </Box>
      <Fade in={isScrolling} timeout={{ enter: 150, exit: 400 }}>
        <Chip
          className={styles.pageIndicatorChip}
          color="primary"
          label={`Page ${currentPosition} / ${pages.length}`}
        />
      </Fade>
      <Stack className={styles.pageStack}>
        {pages.map((page) => (
          <img
            key={page.id}
            ref={(el) => {
              if (el) imageRefs.current.set(page.position, el);
              else imageRefs.current.delete(page.position);
            }}
            src={page.cover}
            alt={page.position.toString()}
            data-position={page.position}
            className={styles.pageImage}
          />
        ))}
      </Stack>
    </Container>
  );
}
