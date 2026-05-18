/**
 * Shared Axios client wired to `VITE_API_HOST`, JSON defaults, and bearer auth from the
 * `accessToken` cookie.
 */

import axios from 'axios';
import Cookies from 'js-cookie';

import { useMainStore } from '@store/main';

/**
 * Pre-configured Axios instance for all API helpers. Every outgoing request runs through a request
 * interceptor that requires `accessToken` in cookies: when it is missing, the user is redirected to
 * `/login?redirectTo=<current path>` and the request is aborted; when present, `Authorization` is set
 * to `Bearer <token>`.
 */
export const apiClientInstance = axios.create({
  baseURL: import.meta.env.VITE_API_HOST ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Runs before every `apiClientInstance` request: attaches the bearer token or triggers login redirect.
 */
apiClientInstance.interceptors.request.use((config) => {
  const accessToken = Cookies.get('accessToken');

  if (!accessToken) {
    const fullRedirectUrl = `/login?redirectTo=${encodeURIComponent(window.location.pathname)}`;
    window.location.href = fullRedirectUrl;
    throw new Error('Unauthorized');
  }

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

/**
 * React hook that exposes a small async wrapper around imperative API calls. While the wrapped
 * promise runs, the `useMainStore` loading flag is toggled on; it is cleared afterward (including
 * after errors). Failures are logged to the console then rethrown.
 *
 * @returns An object with a `wrapper` method for guarding async work with global loading state.
 */
export const useApiClientWrapper = () => {
  const setIsLoading = useMainStore((state) => state.setIsLoading);

  return {
    /**
     * Runs `func` with global loading state (`setIsLoading`) set to true for the duration.
     *
     * @typeParam T - Resolved value type of the wrapped call.
     * @param {() => Promise<T>} func - Typically a closure that invokes `apiClientInstance`.
     * @returns {Promise<T>} The settled result of `func`, or rethrows after logging on rejection.
     */
    wrapper: async <T>(func: () => Promise<T>): Promise<T> => {
      try {
        setIsLoading(true);
        const response = await func();
        return response;
      } catch (error) {
        console.error('Error:', error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
  };
};
