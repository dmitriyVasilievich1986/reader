/**
 * Public entry for the author API client: re-exports {@link useAuthorAPIClient} and {@link SimpleAuthorType}.
 *
 * @module services/apiClient/author/index
 */

import { useAuthorAPIClient } from './client';

import type { SimpleAuthorType } from './types';

export { useAuthorAPIClient, type SimpleAuthorType };
