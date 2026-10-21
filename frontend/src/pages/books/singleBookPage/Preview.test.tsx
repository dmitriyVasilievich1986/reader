/**
 * Tests for {@link BookPreview}: page request, loading skeletons and opening the reader at a page.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { BookPreview } from './Preview';

const { getPages } = vi.hoisted(() => ({ getPages: vi.fn() }));

vi.mock('@services/apiClient/page', () => ({
  usePageAPIClient: () => ({ getPages }),
}));

const pages = [
  { id: 11, cover: '/images/p1.png', position: 1 },
  { id: 12, cover: '/images/p2.png', position: 2 },
];

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname + location.search}</div>;
}

function renderPreview(bookId = 7) {
  return render(
    <MemoryRouter initialEntries={['/preview']}>
      <Routes>
        <Route path="/preview" element={<BookPreview bookId={bookId} />} />
        <Route path="*" element={<LocationDisplay />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('BookPreview', () => {
  beforeEach(() => {
    getPages.mockResolvedValue({ data: pages });
  });

  it('requests the first four pages of the book', async () => {
    renderPreview();

    await screen.findByRole('img', { name: '1' });
    expect(getPages).toHaveBeenCalledWith(4, 0, 'position', 'asc', [
      { column: 'book_id', operator: 'eq', value: 7 },
    ]);
  });

  it('shows skeletons while pages are loading', () => {
    getPages.mockReturnValue(new Promise(() => {}));
    const { container } = renderPreview();

    expect(container.querySelectorAll('.MuiSkeleton-root')).toHaveLength(5);
  });

  it('does not request pages without a book id', () => {
    renderPreview(0);

    expect(getPages).not.toHaveBeenCalled();
  });

  it('renders page thumbnails in order', async () => {
    renderPreview();

    await screen.findByRole('img', { name: '1' });
    expect(screen.getAllByRole('img').map((img) => img.getAttribute('alt'))).toEqual(['1', '2']);
  });

  it('opens the reader at the clicked page', async () => {
    const user = userEvent.setup();
    renderPreview();

    await user.click(await screen.findByRole('img', { name: '2' }));

    expect(screen.getByTestId('location')).toHaveTextContent('/book/7/read?page=2');
  });
});
