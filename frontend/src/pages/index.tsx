/**
 * Barrel module for the pages: re-exports {@link BooksPage}, {@link SingleBookPage}, {@link ReadBookPage}, {@link HomePage}, {@link Login}, {@link ProfileForm}, {@link Authors}.
 *
 * @module pages/index
 */

import { Authors } from './authors';
import { SingleBookPage, BooksPage, ReadBookPage } from './books';
import { HomePage } from './home/HomePage';
import { Login } from './login/Login';
import { ProfileForm } from './profile/ProfileForm';

export { BooksPage, SingleBookPage, ReadBookPage, HomePage, Login, ProfileForm, Authors };
