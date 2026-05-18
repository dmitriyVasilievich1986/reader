/**
 * Barrel module for the books: re-exports {@link ReadBookPage}, {@link SingleBookPage}, {@link BooksPage}.
 *
 * @module pages/books/index
 */

import { BooksPage } from './BooksPage';
import { ReadBookPage } from './readBookPage';
import { SingleBookPage } from './singleBookPage';

export { ReadBookPage, SingleBookPage, BooksPage };
