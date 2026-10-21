/**
 * Tests for {@link usePageAPIClient}: paginated page list requests.
 */

import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { apiClientInstance } from '../base';
import { usePageAPIClient } from './client';

const pages = [{ id: 11, cover: '/images/p1.png', position: 1 }];
const metadata = { total: 1, offset: 0, limit: 4, sort_by: 'position', sort_order: 'asc' };

describe('usePageAPIClient', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches pages with JSON-encoded filters', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue({ data: { data: pages, metadata } });
    const filters = [{ column: 'book_id', operator: 'eq', value: 7 }];

    await expect(usePageAPIClient().getPages(4, 0, 'position', 'asc', filters)).resolves.toEqual({
      data: pages,
      metadata,
    });
    expect(get).toHaveBeenCalledWith('/api/v1/page', {
      params: {
        limit: 4,
        offset: 0,
        sortBy: 'position',
        sortOrder: 'asc',
        filters: JSON.stringify(filters),
      },
    });
  });

  it('leaves out filters when none are given', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue({ data: { data: [], metadata } });

    await usePageAPIClient().getPages();

    expect(get).toHaveBeenCalledWith('/api/v1/page', {
      params: {
        limit: undefined,
        offset: undefined,
        sortBy: undefined,
        sortOrder: undefined,
        filters: undefined,
      },
    });
  });
});
