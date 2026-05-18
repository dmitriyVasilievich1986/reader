/**
 * Public entry for the page API client: re-exports {@link usePageAPIClient} and {@link PageType}.
 *
 * @module services/apiClient/page/index
 */

import { usePageAPIClient } from './client';

import type { PageType } from './types';

export { usePageAPIClient, type PageType };
