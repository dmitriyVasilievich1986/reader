/**
 * Barrel module for the books: re-exports {@link ReadBookPage}, {@link SinlgeBookPage}, {@link BooksPage}.
 *
 * @module pages/books/index
 */

import { BooksPage } from './BooksPage';
import { ReadBookPage } from './readBookPage';
import { SinlgeBookPage } from './sinlgeBookPage';

export { ReadBookPage, SinlgeBookPage, BooksPage };
