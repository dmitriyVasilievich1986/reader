/**
 * Public entry for the API client: re-exports {@link useAuthAPIClient}, {@link useUserAPIClient}, {@link useBookAPIClient}, {@link usePageAPIClient}, {@link useAuthorAPIClient}.
 *
 * @module services/apiClient/index
 */

import { useAuthAPIClient } from './auth/client';
import { useAuthorAPIClient } from './author/client';
import { useBookAPIClient } from './book/client';
import { usePageAPIClient } from './page/client';
import { useUserAPIClient } from './user/client';

export {
  useAuthAPIClient,
  useUserAPIClient,
  useBookAPIClient,
  usePageAPIClient,
  useAuthorAPIClient,
};
