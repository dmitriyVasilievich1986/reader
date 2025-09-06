export enum AvailableMenus {
  Category = "Category",
  Author = "Author",
  Books = "Books",
  Book = "Book",
  Pages = "Pages",
  Page = "Page",
  Home = "Home",
}

export type MenuType = {
  label: AvailableMenus;
  url: string;
};

export type PathNameType = {
  label: string;
  to: string;
};
