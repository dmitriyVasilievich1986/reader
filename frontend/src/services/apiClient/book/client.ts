/**
 * Book API helpers using the shared authenticated axios instance (`apiClientInstance`).
 */

import { apiClientInstance } from '../base';

import type { SimpleBookType, BookType } from './types';
import type { PaginationMetadata, FilterType } from '../types';

/**
 * Factory for book endpoints (`/api/v1/book`).
 *
 * @returns Methods to fetch one book or a paginated list.
 */
export const useBookAPIClient = () => {
  return {
    /**
     * GET `/api/v1/book/:bookId` — returns a single {@link BookType}.
     *
     * @param bookId - Primary key of the book.
     */
    getBook: async (bookId: number): Promise<BookType> => {
      const response = await apiClientInstance.get<BookType>(`/api/v1/book/${bookId}`);
      return response.data;
    },
    /**
     * GET `/api/v1/book` with optional pagination, sort, and JSON-encoded `filters` query param.
     *
     * @param limit - Page size (passed through when set).
     * @param offset - Skip count (passed through when set).
     * @param sortBy - Sort field name (passed through when set).
     * @param sortOrder - Sort direction (passed through when set).
     * @param filters - Column filters serialized to JSON in `params.filters` when non-empty.
     */
    getBooks: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: SimpleBookType[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: SimpleBookType[];
        metadata: PaginationMetadata;
      }>(`/api/v1/book`, {
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
