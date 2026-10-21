/**
 * Tests for the {@link HomePage}: popular and newest book requests, loading skeletons and navigation.
 */

import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { HomePage } from './HomePage';

import type { BookType } from '@services/apiClient/book';

const { getBooks } = vi.hoisted(() => ({ getBooks: vi.fn() }));

vi.mock('@services/apiClient/book', () => ({
  useBookAPIClient: () => ({ getBooks }),
}));

const makeBook = (id: number, name: string): BookType => ({
  id,
  name,
  authorId: id,
  slug: name.toLowerCase().replaceAll(' ', '-'),
  watchesCount: 0,
  cover: `/images/${id}.png`,
  description: null,
  author: { id, firstName: 'Author', lastName: String(id) },
});

const popularBooks = [makeBook(1, 'War and Peace'), makeBook(2, 'Anna Karenina')];
const newestBooks = [makeBook(3, 'Resurrection')];

/** Resolves `getBooks` by sort field so each section gets its own list. */
const mockBooksBySort = (books: Record<string, Promise<{ data: BookType[] }>>) => {
  getBooks.mockImplementation(
    (_limit: number, _offset: number, sortBy: string) => books[sortBy] ?? new Promise(() => {})
  );
};

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderHomePage() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="*" element={<LocationDisplay />} />
      </Routes>
    </MemoryRouter>
  );
}

const skeletonCount = (container: HTMLElement) =>
  container.querySelectorAll('.MuiSkeleton-root').length;

describe('HomePage', () => {
  beforeEach(() => {
    mockBooksBySort({
      watches_count: Promise.resolve({ data: popularBooks }),
      created_at: Promise.resolve({ data: newestBooks }),
    });
  });

  it('requests the five most popular and five newest books', async () => {
    renderHomePage();

    await screen.findByText('War and Peace');
    expect(getBooks).toHaveBeenCalledTimes(2);
    expect(getBooks).toHaveBeenCalledWith(5, 0, 'watches_count', 'desc');
    expect(getBooks).toHaveBeenCalledWith(5, 0, 'created_at', 'desc');
  });

  it('shows skeletons for both sections while loading', () => {
    mockBooksBySort({});
    const { container } = renderHomePage();

    expect(screen.getByText('Popular Books')).toBeInTheDocument();
    expect(screen.getByText('Newest Books')).toBeInTheDocument();
    expect(skeletonCount(container)).toBe(10);
  });

  it('renders popular books first and newest books second', async () => {
    const { container } = renderHomePage();

    await screen.findByText('Resurrection');
    const infoButtons = screen.getAllByRole('button', { name: /^info about/ });
    expect(infoButtons.map((button) => button.getAttribute('aria-label'))).toEqual([
      'info about War and Peace',
      'info about Anna Karenina',
      'info about Resurrection',
    ]);
    expect(screen.getByText('By Author 1')).toBeInTheDocument();
    expect(skeletonCount(container)).toBe(0);
  });

  it('renders each section as soon as its own request resolves', async () => {
    mockBooksBySort({ watches_count: Promise.resolve({ data: popularBooks }) });
    const { container } = renderHomePage();

    expect(await screen.findByText('War and Peace')).toBeInTheDocument();
    expect(screen.queryByText('Resurrection')).not.toBeInTheDocument();
    expect(skeletonCount(container)).toBe(5);
  });

  it('opens a book page when a book is clicked', async () => {
    const user = userEvent.setup();
    renderHomePage();

    const item = (await screen.findByText('Resurrection')).closest('li');
    expect(item).not.toBeNull();
    await user.click(within(item!).getByRole('img', { name: 'Resurrection' }));

    expect(screen.getByTestId('location')).toHaveTextContent('/book/resurrection');
  });
});
