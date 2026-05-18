/**
 * User REST API client hook: `GET /api/v1/user/me` for the current profile; `PUT /api/v1/user` applies updates
 * and writes the returned user into the main store.
 *
 * @module services/apiClient/user/client
 */

import { useMainStore } from '@store/main/mainStore';
import type { UserType } from '@store/main/types';

import { apiClientInstance, useApiClientWrapper } from '../base';

import type { UserPutRequest } from './types';

/**
 * Hook that exposes user profile requests, using `useApiClientWrapper` for PUT and syncing the main store after a successful update.
 *
 * @returns Object with `getUser` and `putUser` async methods.
 */
export const useUserAPIClient = () => {
  const { wrapper } = useApiClientWrapper();
  const { setUser } = useMainStore();

  return {
    /**
     * Fetches the authenticated user (`GET /api/v1/user/me`). Does not update the global store — callers own persistence.
     *
     * @returns {Promise<UserType>} Current user payload from the API.
     */
    getUser: async () => {
      const response = await apiClientInstance.get<UserType>('/api/v1/user/me');
      return response.data;
    },
    /**
     * Sends a full profile update (`PUT /api/v1/user`) and passes the response to `setUser` so the main store matches the server.
     *
     * @param request - Body with `firstName`, `lastName`, and `photoUrl`.
     * @returns {Promise<UserType>} Updated user returned by the API (also written to the store).
     */
    putUser: async (request: UserPutRequest) => {
      return wrapper(async () => {
        const response = await apiClientInstance.put<UserType>('/api/v1/user', request);
        setUser(response.data);
        return response.data;
      });
    },
    /**
     * Fetches the available pages (`GET /api/v1/user/available-pages`).
     *
     * @returns {Promise<string[]>} Available pages.
     */
    getAvailablePages: async () => {
      const response = await apiClientInstance.get<string[]>('/api/v1/user/available-pages');
      return response.data;
    },
  };
};
