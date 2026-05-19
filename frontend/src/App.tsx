/**
 * App.tsx
 *
 * This file contains the App component, which is the root component of the application.
 * It renders the Navbar and the Routes.
 *
 * @returns {JSX.Element} Top-level Material UI `Box` wrapping navigation and the active route outlet.
 */

import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router';

import { Navbar } from './components';

const HomePage = lazy(() => import('@pages/home').then((m) => ({ default: m.HomePage })));
const LoginPage = lazy(() => import('@pages/login').then((m) => ({ default: m.Login })));
const BooksPage = lazy(() => import('@pages/books').then((m) => ({ default: m.BooksPage })));
const ReadBookPage = lazy(() => import('@pages/books').then((m) => ({ default: m.ReadBookPage })));
const ProfilePage = lazy(() => import('@pages/profile').then((m) => ({ default: m.Profile })));
const AuthorsPage = lazy(() => import('@pages/authors').then((m) => ({ default: m.Authors })));
const SingleBookPage = lazy(() =>
  import('@pages/books').then((m) => ({ default: m.SingleBookPage }))
);
/**
 * Root shell: renders a persistent `Navbar` and `Routes`. Library pages (`HomePage`, login, book list,
 * detail, reader) load on demand via `React.lazy()` and code-split bundles.
 *
 * Route shape: `/` home, `/login` auth UI, `/book` book grid, `/book/:bookId` preview, `/book/:bookId/read` reader.
 *
 * @returns {JSX.Element} Top-level Material UI `Box` wrapping navigation and the active route outlet.
 */
function App() {
  return (
    <Box>
      <Navbar />
      <Suspense
        fallback={
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        }
      >
        <Routes>
          <Route path="" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />

          <Route path="/book">
            <Route path="" element={<BooksPage />} />
            <Route path=":bookId" element={<SingleBookPage />} />
            <Route path=":bookId/read" element={<ReadBookPage />} />
          </Route>
          <Route path="/author" element={<AuthorsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </Suspense>
    </Box>
  );
}

export default App;
