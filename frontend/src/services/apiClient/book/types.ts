import type { SimpleAuthorType } from '../author/types';

/**
 * Lightweight book record for lists and references (mirrors book fields exposed by the API).
 *
 * @property {number} id - Book primary key.
 * @property {string} name - Book title or unique display name.
 * @property {number} authorId - Owning author identifier (`author.id`).
 * @property {string} slug - URL slug of the book.
 * @property {number} watchesCount - Number of times the book has been watched.
 * @property {string} cover - Cover image URL, or null when unset.
 * @property {(string | null)} description - Summary or full description, or null when absent.
 */
export type SimpleBookType = {
  id: number;
  name: string;
  authorId: number;
  slug: string;
  watchesCount: number;
  cover: string;
  description: string | null;
};

export type BookType = SimpleBookType & {
  author: SimpleAuthorType;
};
