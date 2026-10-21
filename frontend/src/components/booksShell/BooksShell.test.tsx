/**
 * Tests for {@link BooksShell}: loading skeletons, book tiles and navigation to a book.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { describe, expect, it } from 'vite-plus/test';

import { BooksShell } from './BooksShell';

import type { BookType } from '@services/apiClient/book';

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
  {
    id: 2,
    name: 'The Iliad',
    authorId: 2,
    slug: 'the-iliad',
    watchesCount: 0,
    cover: '/images/2.png',
    description: null,
    author: { id: 2, firstName: 'Homer', lastName: null },
  },
];

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderBooksShell(shellBooks: BookType[] | null) {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<BooksShell books={shellBooks} />} />
        <Route path="*" element={<LocationDisplay />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('BooksShell', () => {
  it('shows five skeletons while books are loading', () => {
    const { container } = renderBooksShell(null);

    expect(container.querySelectorAll('.MuiSkeleton-root')).toHaveLength(5);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('renders a tile per book with cover, title and author', () => {
    renderBooksShell(books);

    expect(screen.getByRole('img', { name: 'War and Peace' })).toBeInTheDocument();
    expect(screen.getByText('War and Peace')).toBeInTheDocument();
    expect(screen.getByText('By Leo Tolstoy')).toBeInTheDocument();
    expect(screen.getByText('By Homer')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'info about The Iliad' })).toBeInTheDocument();
    expect(screen.getAllByRole('listitem')).toHaveLength(2);
  });

  it('renders an empty grid for an empty list', () => {
    const { container } = renderBooksShell([]);

    expect(screen.queryAllByRole('listitem')).toHaveLength(0);
    expect(container.querySelectorAll('.MuiSkeleton-root')).toHaveLength(0);
  });

  it('opens the book page by slug when a tile is clicked', async () => {
    const user = userEvent.setup();
    renderBooksShell(books);

    await user.click(screen.getByText('The Iliad'));

    expect(screen.getByTestId('location')).toHaveTextContent('/book/the-iliad');
  });
});
