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
  views: number;
  author_name: string;
  description: string;
  created_at: string;
  updated_at: string;
};
