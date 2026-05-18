/**
 * Axios-based auth API calls (login). Uses `VITE_API_HOST` as the request origin.
 */

import axios from 'axios';

import { useApiClientWrapper } from '../base';

import type { LoginResponse } from './types';

/**
 * Factory for auth endpoint helpers. Naming follows other API hooks (`use*`).
 *
 * @returns Auth methods keyed by operation (e.g. `login`).
 */
export const useAuthAPIClient = () => {
  const { wrapper } = useApiClientWrapper();

  return {
    /**
     * POST `/api/v1/user/login` with JSON body; returns parsed {@link LoginResponse}.
     *
     * @param username - Account username.
     * @param password - Account password.
     */
    login: async (username: string, password: string) => {
      const apiHost = import.meta.env.VITE_API_HOST ?? '';
      return wrapper(async () => {
        const response = await axios.post<LoginResponse>(
          `${apiHost}/api/v1/user/login`,
          {
            username,
            password,
          },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );
        return response.data;
      });
    },
  };
};
