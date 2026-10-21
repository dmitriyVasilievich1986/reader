/**
 * Tests for the {@link BooksPage}: page/filters URL params, API paging and the pagination control.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { BooksPage } from './BooksPage';

import type { BookType } from '@services/apiClient/book';

const { getBooks } = vi.hoisted(() => ({ getBooks: vi.fn() }));

vi.mock('@services/apiClient/book', () => ({
  useBookAPIClient: () => ({ getBooks }),
}));

const books: BookType[] = [
  {
    id: 1,
    name: 'War and Peace',
    authorId: 1,
    slug: 'war-and-peace',
    watchesCount: 0,
    cover: '/images/1.png',
    description: null,
    author: { id: 1, firstName: 'Leo', lastName: 'Tolstoy' },
  },
];

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-search">{location.search}</div>;
}

function renderBooksPage(initialEntry = '/book') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <BooksPage />
      <LocationDisplay />
    </MemoryRouter>
  );
}

const filters = [{ column: 'author_id', operator: 'eq', value: 1 }];

describe('BooksPage', () => {
  beforeEach(() => {
    getBooks.mockResolvedValue({
      data: books,
      metadata: { total: 35, offset: 0, limit: 10, sort_by: 'created_at', sort_order: 'desc' },
    });
  });

  it('sets page=1 when the page param is missing and fetches the first page', async () => {
    renderBooksPage();

    expect(await screen.findByText('War and Peace')).toBeInTheDocument();
    expect(screen.getByTestId('location-search')).toHaveTextContent('?page=1');
    expect(getBooks).toHaveBeenCalledWith(10, 0, 'created_at', 'desc', undefined);
  });

  it('fetches the page and filters from the URL', async () => {
    renderBooksPage(`/book?page=3&filters=${encodeURIComponent(JSON.stringify(filters))}`);

    await screen.findByText('War and Peace');
    expect(getBooks).toHaveBeenCalledWith(10, 20, 'created_at', 'desc', filters);
  });

  it('shows skeletons while books are loading', () => {
    getBooks.mockReturnValue(new Promise(() => {}));
    const { container } = renderBooksPage('/book?page=1');

    expect(container.querySelectorAll('.MuiSkeleton-root')).toHaveLength(5);
  });

  it('renders one pagination page per ten books and marks the current one', async () => {
    renderBooksPage('/book?page=2');

    await screen.findByText('War and Peace');
    expect(screen.getByRole('button', { name: 'page 2' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('button', { name: 'Go to page 4' })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Go to page 5' })).not.toBeInTheDocument();
  });

  it('changes page and refetches while keeping the filters', async () => {
    const user = userEvent.setup();
    const encodedFilters = encodeURIComponent(JSON.stringify(filters));
    renderBooksPage(`/book?page=1&filters=${encodedFilters}`);

    await user.click(await screen.findByRole('button', { name: 'Go to page 2' }));

    const search = new URLSearchParams(screen.getByTestId('location-search').textContent ?? '');
    expect(search.get('page')).toBe('2');
    expect(search.get('filters')).toBe(JSON.stringify(filters));
    await waitFor(() => {
      expect(getBooks).toHaveBeenLastCalledWith(10, 10, 'created_at', 'desc', filters);
    });
  });
});
