/**
 * Public entry for the book API client: re-exports {@link useBookAPIClient} and {@link SimpleBookType}.
 *
 * @module services/apiClient/book/index
 */

import { useBookAPIClient } from './client';

import type { SimpleBookType, BookType } from './types';

export { useBookAPIClient, type SimpleBookType, type BookType };
