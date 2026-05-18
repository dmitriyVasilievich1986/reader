/**
 * Page API payload types (paginated reader pages within a book).
 */

/**
 * Single page row returned by page list/detail endpoints.
 *
 * @property {number} id - Page primary key.
 * @property {string} cover - URL or path to the page image asset.
 * @property {number} position - Ordinal position of this page within its book.
 */
export type PageType = {
  id: number;
  cover: string;
  position: number;
};
