/**
 * Tests for {@link useAuthorAPIClient}: single author and paginated list requests.
 */

import { afterEach, describe, expect, it, vi } from 'vite-plus/test';

import { apiClientInstance } from '../base';
import { useAuthorAPIClient } from './client';

const author = { id: 1, firstName: 'Leo', lastName: 'Tolstoy' };
const metadata = { total: 1, offset: 0, limit: 10, sort_by: 'id', sort_order: 'asc' };

describe('useAuthorAPIClient', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches a single author by id', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue({ data: author });

    await expect(useAuthorAPIClient().getAuthor(1)).resolves.toEqual(author);
    expect(get).toHaveBeenCalledWith('/api/v1/author/1');
  });

  it('fetches a page of authors with JSON-encoded filters', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue({ data: { data: [author], metadata } });
    const filters = [{ column: 'name', operator: 'ilike', value: 'tol' }];

    await expect(useAuthorAPIClient().getAuthors(10, 20, 'name', 'desc', filters)).resolves.toEqual(
      { data: [author], metadata }
    );
    expect(get).toHaveBeenCalledWith('/api/v1/author', {
      params: {
        limit: 10,
        offset: 20,
        sortBy: 'name',
        sortOrder: 'desc',
        filters: JSON.stringify(filters),
      },
    });
  });

  it('leaves out filters and unset params', async () => {
    const get = vi
      .spyOn(apiClientInstance, 'get')
      .mockResolvedValue({ data: { data: [], metadata } });

    await useAuthorAPIClient().getAuthors();

    expect(get).toHaveBeenCalledWith('/api/v1/author', {
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
