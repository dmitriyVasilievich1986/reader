export type PageType = {
  id: number;
  cover: string;
  position: number;
};

export type AuthorType = {
  id: number;
  name: string;
  last_name: string;
  first_name: string;
};

export type BookType = {
  id: number;
  name: string;
  cover: string;
  author_name: string;
  description: string;
};
