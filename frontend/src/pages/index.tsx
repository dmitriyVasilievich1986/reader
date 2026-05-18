/**
 * Barrel module for the pages: re-exports {@link BooksPage}, {@link SinlgeBookPage}, {@link ReadBookPage}, {@link HomePage}, {@link Login}, {@link PagesPage}.
 */

import { SinlgeBookPage, BooksPage, ReadBookPage } from './books';
import { HomePage } from './home/HomePage';
import { Login } from './login/Login';
import { PagesPage } from './pages/PagesPage';

export { BooksPage, SinlgeBookPage, ReadBookPage, HomePage, Login, PagesPage };
