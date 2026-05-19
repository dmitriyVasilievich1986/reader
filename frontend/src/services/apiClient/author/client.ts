/**
 * Author API helpers using the shared authenticated axios instance (`apiClientInstance`).
 */

import { apiClientInstance } from '../base';

import type { SimpleAuthorType } from './types';
import type { PaginationMetadata, FilterType } from '../types';

/**
 * Factory for author endpoints (`/api/v1/author`).
 *
 * @returns Methods to fetch one author or a paginated list.
 */
export const useAuthorAPIClient = () => {
  return {
    /**
     * GET `/api/v1/author/:authorId` — returns a single {@link SimpleAuthorType}.
     *
     * @param authorId - Primary key of the author.
     */
    getAuthor: async (authorId: number): Promise<SimpleAuthorType> => {
      const response = await apiClientInstance.get<SimpleAuthorType>(`/api/v1/author/${authorId}`);
      return response.data;
    },
    /**
     * GET `/api/v1/author` with optional pagination, sort, and JSON-encoded `filters` query param.
     *
     * @param limit - Page size (passed through when set).
     * @param offset - Skip count (passed through when set).
     * @param sortBy - Sort field name (passed through when set).
     * @param sortOrder - Sort direction (passed through when set).
     * @param filters - Column filters serialized to JSON in `params.filters` when non-empty.
     */
    getAuthors: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: SimpleAuthorType[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: SimpleAuthorType[];
        metadata: PaginationMetadata;
      }>(`/api/v1/author`, {
        params: {
          limit,
          offset,
          sortBy,
          sortOrder,
          filters: filters ? JSON.stringify(filters) : undefined,
        },
      });
      return { data: response.data.data, metadata: response.data.metadata };
    },
  };
};
