import type { SimpleAuthorType } from '@services/apiClient/author';

/**
 * Formats an author's display name from first and last name fields.
 *
 * Returns only `firstName` when `lastName` is null or empty; otherwise
 * `"${firstName} ${lastName}"`.
 *
 * @param author - Author record with `firstName` and optional `lastName`.
 * @returns Human-readable full or given name.
 */
export function getAuthorName(author: SimpleAuthorType): string {
  if (!author.lastName) {
    return author.firstName;
  }
  return `${author.firstName} ${author.lastName}`;
}
