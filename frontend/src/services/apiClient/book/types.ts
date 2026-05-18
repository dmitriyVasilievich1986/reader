/**
 * Book-related API payload types (list/detail summaries).
 */

export type SimpleAuthorType = {
  id: number;
  firstName: string;
  lastName: string | null;
};

/**
 * Lightweight book record for lists and references (mirrors book fields exposed by the API).
 *
 * @property {number} id - Book primary key.
 * @property {string} name - Book title or unique display name.
 * @property {number} authorId - Owning author identifier (`author.id`).
 * @property {string} cover - Cover image URL, or null when unset.
 * @property {(string | null)} description - Summary or full description, or null when absent.
 */
export type SimpleBookType = {
  id: number;
  name: string;
  authorId: number;
  cover: string;
  description: string | null;
};

export type BookType = SimpleBookType & {
  author: SimpleAuthorType;
};
