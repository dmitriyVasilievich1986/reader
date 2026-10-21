/**
 * Tests for the {@link Authors} page: loading state, URL search params, API calls and pagination.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { Authors } from './Authors';

import type { SimpleAuthorType } from '@services/apiClient/author';

const getAuthors = vi.fn();

vi.mock('@services/apiClient/author', () => ({
  useAuthorAPIClient: () => ({ getAuthors }),
}));

const authors: SimpleAuthorType[] = [
  { id: 1, firstName: 'Leo', lastName: 'Tolstoy' },
  { id: 2, firstName: 'Homer', lastName: null },
];

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-search">{location.search}</div>;
}

function renderAuthors(initialEntry = '/author') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Authors />
      <LocationDisplay />
    </MemoryRouter>
  );
}

describe('Authors', () => {
  beforeEach(() => {
    getAuthors.mockResolvedValue({
      data: authors,
      metadata: { total: 25, offset: 0, limit: 10, sort_by: 'id', sort_order: 'asc' },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows a skeleton while authors are loading', () => {
    getAuthors.mockReturnValue(new Promise(() => {}));
    renderAuthors('/author?page=0');

    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('sets page=0 when the page param is missing and fetches the first page', async () => {
    renderAuthors();

    await waitFor(() => {
      expect(screen.getByTestId('location-search')).toHaveTextContent('?page=0');
    });
    await waitFor(() => {
      expect(getAuthors).toHaveBeenCalledWith(10, 0, undefined, undefined, undefined);
    });
  });

  it('renders author names linking to their filtered books', async () => {
    renderAuthors('/author?page=0');

    const tolstoy = await screen.findByRole('link', { name: 'Leo Tolstoy' });
    const homer = screen.getByRole('link', { name: 'Homer' });

    const filtersFor = (id: number) =>
      JSON.stringify([{ column: 'author_id', operator: 'eq', value: id }]);
    expect(tolstoy).toHaveAttribute('href', `/book?filters=${filtersFor(1)}`);
    expect(homer).toHaveAttribute('href', `/book?filters=${filtersFor(2)}`);
    expect(screen.getByText('1–10 of 25')).toBeInTheDocument();
  });

  it('passes page, sort and search params to the API', async () => {
    renderAuthors('/author?page=2&sortBy=name&sortOrder=desc&search=tol');

    await waitFor(() => {
      expect(getAuthors).toHaveBeenCalledWith(10, 20, 'name', 'desc', [
        { column: 'name', operator: 'ilike', value: 'tol' },
      ]);
    });
  });

  it('moves to the next page and refetches', async () => {
    const user = userEvent.setup();
    renderAuthors('/author?page=0');

    await user.click(await screen.findByRole('button', { name: /next page/i }));

    expect(screen.getByTestId('location-search')).toHaveTextContent('?page=1');
    await waitFor(() => {
      expect(getAuthors).toHaveBeenLastCalledWith(10, 10, undefined, undefined, undefined);
    });
  });

  it('renders an empty table when the request fails', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    getAuthors.mockRejectedValue(new Error('Network error'));
    renderAuthors('/author?page=0');

    expect(await screen.findByRole('table')).toBeInTheDocument();
    expect(screen.queryAllByRole('link')).toHaveLength(0);
    expect(screen.getByText('0–0 of 0')).toBeInTheDocument();
    expect(consoleError).toHaveBeenCalledWith('Error fetching authors:', expect.any(Error));
  });
});
