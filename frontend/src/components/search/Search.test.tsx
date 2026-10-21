/**
 * Tests for {@link Search}: initial value from the URL and committing the query on Enter or icon click.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router';
import { describe, expect, it } from 'vite-plus/test';

import { Search } from './Search';

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location-search">{location.search}</div>;
}

function renderSearch(initialEntry = '/author?page=3', paramName?: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Search label="Search authors" paramName={paramName} />
      <LocationDisplay />
    </MemoryRouter>
  );
}

const searchParams = () =>
  new URLSearchParams(screen.getByTestId('location-search').textContent ?? '');

describe('Search', () => {
  it('starts with the value from the URL', () => {
    renderSearch('/author?search=tol');

    expect(screen.getByLabelText('Search authors')).toHaveValue('tol');
  });

  it('does not touch the URL while typing', async () => {
    const user = userEvent.setup();
    renderSearch();

    await user.type(screen.getByLabelText('Search authors'), 'tol');

    expect(searchParams().get('search')).toBeNull();
    expect(searchParams().get('page')).toBe('3');
  });

  it('sets the search param and resets the page on Enter', async () => {
    const user = userEvent.setup();
    renderSearch();

    await user.type(screen.getByLabelText('Search authors'), 'tol{Enter}');

    expect(searchParams().get('search')).toBe('tol');
    expect(searchParams().get('page')).toBe('0');
  });

  it('searches when the icon is clicked', async () => {
    const user = userEvent.setup();
    const { container } = renderSearch();

    await user.type(screen.getByLabelText('Search authors'), 'tol');
    await user.click(container.querySelector('[data-testid="SearchIcon"]')!);

    expect(searchParams().get('search')).toBe('tol');
  });

  it('removes the search param when the query is cleared', async () => {
    const user = userEvent.setup();
    renderSearch('/author?search=tol&page=2');

    await user.clear(screen.getByLabelText('Search authors'));
    await user.keyboard('{Enter}');

    expect(searchParams().has('search')).toBe(false);
    expect(searchParams().get('page')).toBe('0');
  });

  it('uses a custom param name', async () => {
    const user = userEvent.setup();
    renderSearch('/book?q=war', 'q');

    expect(screen.getByLabelText('Search authors')).toHaveValue('war');
    await user.type(screen.getByLabelText('Search authors'), ' and peace{Enter}');

    expect(searchParams().get('q')).toBe('war and peace');
    expect(searchParams().has('search')).toBe(false);
  });
});
