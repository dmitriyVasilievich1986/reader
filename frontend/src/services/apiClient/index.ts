/**
 * Public entry for the API client: re-exports {@link useAuthAPIClient}, {@link useUserAPIClient}, {@link useBookAPIClient}, {@link usePageAPIClient}.
 *
 * @module services/apiClient/index
 */

import { useAuthAPIClient } from './auth/client';
import { useBookAPIClient } from './book/client';
import { usePageAPIClient } from './page/client';
import { useUserAPIClient } from './user/client';

export { useAuthAPIClient, useUserAPIClient, useBookAPIClient, usePageAPIClient };
