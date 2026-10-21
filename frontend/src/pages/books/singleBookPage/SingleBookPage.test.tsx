/**
 * Tests for the {@link SingleBookPage}: loading by slug, book details, preview and the read action.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { SingleBookPage } from './SingleBookPage';

import type { BookType } from '@services/apiClient/book';

const { getBookBySlug, incrementWatchesCount, getPages } = vi.hoisted(() => ({
  getBookBySlug: vi.fn(),
  incrementWatchesCount: vi.fn(),
  getPages: vi.fn(),
}));

vi.mock('@services/apiClient/book', () => ({
  useBookAPIClient: () => ({ getBookBySlug, incrementWatchesCount }),
}));

vi.mock('@services/apiClient/page', () => ({
  usePageAPIClient: () => ({ getPages }),
}));

const book: BookType = {
  id: 7,
  name: 'War and Peace',
  authorId: 1,
  slug: 'war-and-peace',
  watchesCount: 42,
  cover: '/images/7.png',
  description: null,
  author: { id: 1, firstName: 'Leo', lastName: 'Tolstoy' },
};

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderSingleBookPage(slug = 'war-and-peace') {
  return render(
    <MemoryRouter initialEntries={[`/book/${slug}`]}>
      <Routes>
        <Route path="/book/:bookId" element={<SingleBookPage />} />
        <Route path="*" element={<LocationDisplay />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('SingleBookPage', () => {
  beforeEach(() => {
    getBookBySlug.mockResolvedValue(book);
    incrementWatchesCount.mockResolvedValue({ ...book, watchesCount: 43 });
    getPages.mockResolvedValue({ data: [{ id: 11, cover: '/images/p1.png', position: 1 }] });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows a skeleton while the book is loading', () => {
    getBookBySlug.mockReturnValue(new Promise(() => {}));
    const { container } = renderSingleBookPage();

    expect(getBookBySlug).toHaveBeenCalledWith('war-and-peace');
    expect(screen.queryByRole('button', { name: 'Read' })).not.toBeInTheDocument();
    expect(container.querySelectorAll('.MuiSkeleton-root')).toHaveLength(1);
  });

  it('renders the book details', async () => {
    renderSingleBookPage();

    expect(await screen.findByRole('heading', { name: 'War and Peace' })).toBeInTheDocument();
    expect(screen.getByText('Leo Tolstoy')).toBeInTheDocument();
    expect(screen.getByText('42 views')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'War and Peace' })).toBeInTheDocument();
  });

  it('shows only the first name when the author has no last name', async () => {
    getBookBySlug.mockResolvedValue({ ...book, author: { ...book.author, lastName: null } });
    renderSingleBookPage();

    expect(await screen.findByText('Leo')).toBeInTheDocument();
  });

  it('renders the page preview for the book', async () => {
    renderSingleBookPage();

    expect(await screen.findByRole('img', { name: '1' })).toBeInTheDocument();
    expect(getPages).toHaveBeenCalledWith(4, 0, 'position', 'asc', [
      { column: 'book_id', operator: 'eq', value: 7 },
    ]);
  });

  it('counts a view and opens the reader on Read', async () => {
    const user = userEvent.setup();
    renderSingleBookPage();

    await user.click(await screen.findByRole('button', { name: 'Read' }));

    expect(incrementWatchesCount).toHaveBeenCalledWith(7);
    expect(screen.getByTestId('location')).toHaveTextContent('/book/7/read');
  });

  it('still opens the reader when counting the view fails', async () => {
    const user = userEvent.setup();
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('Network error');
    incrementWatchesCount.mockRejectedValue(error);
    renderSingleBookPage();

    await user.click(await screen.findByRole('button', { name: 'Read' }));

    expect(screen.getByTestId('location')).toHaveTextContent('/book/7/read');
    await waitFor(() => {
      expect(consoleError).toHaveBeenCalledWith('Failed to increment watches count', error);
    });
  });
});
