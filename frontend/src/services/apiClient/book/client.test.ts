/**
 * Tests for {@link useBookAPIClient}: book lookups, paginated list and the watch counter.
 */

import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { apiClientInstance } from '../base';
import { useBookAPIClient } from './client';

import type { BookType } from './types';

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
const metadata = { total: 1, offset: 0, limit: 10, sort_by: 'created_at', sort_order: 'desc' };

describe('useBookAPIClient', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches a book by id', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue({ data: book });

    await expect(useBookAPIClient().getBook(7)).resolves.toEqual(book);
    expect(get).toHaveBeenCalledWith('/api/v1/book/7');
  });

  it('fetches a book by slug', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue({ data: book });

    await expect(useBookAPIClient().getBookBySlug('war-and-peace')).resolves.toEqual(book);
    expect(get).toHaveBeenCalledWith('/api/v1/book/slug/war-and-peace');
  });

  it('fetches a page of books with JSON-encoded filters', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue({ data: { data: [book], metadata } });
    const filters = [{ column: 'author_id', operator: 'eq', value: 1 }];

    await expect(
      useBookAPIClient().getBooks(10, 0, 'created_at', 'desc', filters)
    ).resolves.toEqual({ data: [book], metadata });
    expect(get).toHaveBeenCalledWith('/api/v1/book', {
      params: {
        limit: 10,
        offset: 0,
        sortBy: 'created_at',
        sortOrder: 'desc',
        filters: JSON.stringify(filters),
      },
    });
  });

  it('leaves out filters when none are given', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue({ data: { data: [], metadata } });

    await useBookAPIClient().getBooks(5);

    expect(get).toHaveBeenCalledWith('/api/v1/book', {
      params: {
        limit: 5,
        offset: undefined,
        sortBy: undefined,
        sortOrder: undefined,
        filters: undefined,
      },
    });
  });

  it('increments the watch counter', async () => {
    const updated = { ...book, watchesCount: 43 };
    const post = vi.spyOn(apiClientInstance, 'post').mockResolvedValue({ data: updated });

    await expect(useBookAPIClient().incrementWatchesCount(7)).resolves.toEqual(updated);
    expect(post).toHaveBeenCalledWith('/api/v1/book/7/watch');
  });
});
