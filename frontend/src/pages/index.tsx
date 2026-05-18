/**
 * Barrel module for the pages: re-exports {@link BooksPage}, {@link SinlgeBookPage}, {@link ReadBookPage}, {@link HomePage}, {@link Login}.
 */

import { SinlgeBookPage, BooksPage, ReadBookPage } from './books';
import { HomePage } from './home/HomePage';
import { Login } from './login/Login';

export { BooksPage, SinlgeBookPage, ReadBookPage, HomePage, Login };
