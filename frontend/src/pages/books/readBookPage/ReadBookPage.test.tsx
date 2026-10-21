/**
 * Tests for the {@link ReadBookPage}: page request, progress, initial scroll to `?page=`,
 * the scroll-driven page chip and position tracking via `IntersectionObserver`.
 */

import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { ReadBookPage } from './ReadBookPage';

const { getPages } = vi.hoisted(() => ({ getPages: vi.fn() }));

vi.mock('@services/apiClient/page', () => ({
  usePageAPIClient: () => ({ getPages }),
}));

const pages = [
  { id: 11, cover: '/images/p1.png', position: 1 },
  { id: 12, cover: '/images/p2.png', position: 2 },
  { id: 13, cover: '/images/p3.png', position: 3 },
  { id: 14, cover: '/images/p4.png', position: 4 },
];

/** Minimal `IntersectionObserver` stand-in that lets tests report intersecting elements. */
class MockIntersectionObserver {
  static instances: MockIntersectionObserver[] = [];
  observed: Element[] = [];
  disconnect = vi.fn();

  constructor(private callback: IntersectionObserverCallback) {
    MockIntersectionObserver.instances.push(this);
  }

  observe(element: Element) {
    this.observed.push(element);
  }

  intersect(element: Element) {
    this.callback(
      [{ target: element, isIntersecting: true } as unknown as IntersectionObserverEntry],
      this as unknown as IntersectionObserver
    );
  }
}

const latestObserver = () => MockIntersectionObserver.instances.at(-1);

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-search">{location.search}</div>;
}

function renderReadBookPage(initialEntry = '/book/7/read') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route
          path="/book/:bookId/read"
          element={
            <>
              <ReadBookPage />
              <LocationDisplay />
            </>
          }
        />
      </Routes>
    </MemoryRouter>
  );
}

const pageImage = (position: number) => screen.getByRole('img', { name: String(position) });

describe('ReadBookPage', () => {
  const scrollIntoView = vi.fn();

  beforeEach(() => {
    MockIntersectionObserver.instances = [];
    vi.stubGlobal('IntersectionObserver', MockIntersectionObserver);
    Element.prototype.scrollIntoView = scrollIntoView;
    scrollIntoView.mockClear();
    getPages.mockResolvedValue({ data: pages });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('requests all pages of the book in order', async () => {
    renderReadBookPage();

    await screen.findByRole('img', { name: '1' });
    expect(getPages).toHaveBeenCalledWith(100, 0, 'position', 'asc', [
      { column: 'book_id', operator: 'eq', value: 7 },
    ]);
    expect(screen.getAllByRole('img').map((img) => img.getAttribute('alt'))).toEqual([
      '1',
      '2',
      '3',
      '4',
    ]);
  });

  it('starts on the first page without a page param', async () => {
    renderReadBookPage();

    await screen.findByRole('img', { name: '1' });
    expect(screen.getByText('Page 1 / 4')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '25');
    expect(latestObserver()?.observed).toHaveLength(4);
    expect(scrollIntoView).not.toHaveBeenCalled();
  });

  it('scrolls to the page from the URL once the preceding images load', async () => {
    renderReadBookPage('/book/7/read?page=3');

    await screen.findByRole('img', { name: '3' });
    expect(screen.getByText('Page 3 / 4')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '75');
    expect(scrollIntoView).not.toHaveBeenCalled();
    expect(MockIntersectionObserver.instances).toHaveLength(0);

    const target = pageImage(3);
    fireEvent.load(pageImage(1));
    fireEvent.load(pageImage(2));
    await act(async () => {
      fireEvent.load(target);
    });

    expect(scrollIntoView).toHaveBeenCalledOnce();
    expect(scrollIntoView.mock.contexts[0]).toBe(target);
    expect(latestObserver()?.observed).toHaveLength(4);
  });

  it('ignores a page param that does not match any page', async () => {
    renderReadBookPage('/book/7/read?page=9');

    await screen.findByRole('img', { name: '1' });
    expect(scrollIntoView).not.toHaveBeenCalled();
    expect(latestObserver()?.observed).toHaveLength(4);
  });

  it('shows the page chip while scrolling and hides it a second later', async () => {
    renderReadBookPage();
    await screen.findByRole('img', { name: '1' });
    const chip = () => screen.getByText('Page 1 / 4').closest('.MuiChip-root');
    expect(chip()).toHaveStyle({ visibility: 'hidden' });

    vi.useFakeTimers();
    act(() => {
      fireEvent.scroll(window);
    });
    expect(chip()).not.toHaveStyle({ visibility: 'hidden' });

    // The fade-out (400ms) is scheduled only after the 1s scroll timeout re-renders the chip.
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    act(() => {
      vi.advanceTimersByTime(400);
    });
    expect(chip()).toHaveStyle({ visibility: 'hidden' });
  });

  it('tracks the page that crosses the middle of the viewport', async () => {
    renderReadBookPage();
    await screen.findByRole('img', { name: '1' });

    act(() => {
      latestObserver()?.intersect(pageImage(2));
    });

    expect(screen.getByText('Page 2 / 4')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '50');
    expect(screen.getByTestId('location-search')).toHaveTextContent('?page=2');
  });
});
