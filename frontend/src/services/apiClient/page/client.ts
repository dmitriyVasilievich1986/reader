/**
 * Book API helpers using the shared authenticated axios instance (`apiClientInstance`).
 */

import { apiClientInstance } from '../base';

import type { PageType } from './types';
import type { PaginationMetadata, FilterType } from '../types';

/**
 * Factory for page endpoints (`/api/v1/page`).
 *
 * @returns Methods to fetch one page or a paginated list.
 */
export const usePageAPIClient = () => {
  return {
    getPages: async (
      limit?: number,
      offset?: number,
      sortBy?: string,
      sortOrder?: string,
      filters?: FilterType[]
    ): Promise<{ data: PageType[]; metadata: PaginationMetadata }> => {
      const response = await apiClientInstance.get<{
        data: PageType[];
        metadata: PaginationMetadata;
      }>(`/api/v1/page`, {
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
