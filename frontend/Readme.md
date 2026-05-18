# Reader Frontend

React + TypeScript single-page app that consumes the Reader backend API. The
frontend owns the UI for browsing the personal book library — login, book
grid, book detail, and a paginated reader view — and ships its production
bundle into the backend's `static/` directory so it can be served directly by
FastAPI.

---

## Technology stack

| Layer            | Choice                                                  |
| ---------------- | ------------------------------------------------------- |
| Language         | TypeScript 5.6                                          |
| UI framework     | React 18 (StrictMode)                                   |
| Build / dev      | Vite 6 (`@vitejs/plugin-react`)                         |
| Routing          | `react-router` v7                                       |
| Component kit    | MUI (`@mui/material`, `@mui/icons-material`) + Emotion  |
| Styling          | Tailwind CSS 3 (Preflight disabled to coexist with MUI) |
| State management | Zustand (with Redux DevTools middleware)                |
| HTTP client      | Axios + `js-cookie` for bearer-token storage            |
| Utilities        | `dayjs`, `classnames`, `rison`                          |
| Tooling          | ESLint 9 (typescript-eslint, import order), Prettier    |

---

## Project layout

```
frontend/
├── application-version.json    # Injected at build time as VITE_APP_VERSION
├── index.html                  # Vite entry HTML
├── vite.config.ts              # Build config + path aliases + outDir → ../backend/static
├── tailwind.config.js          # Tailwind theme; Preflight disabled (MUI coexists)
├── tsconfig.{json,app.json,node.json}
├── eslint.config.js            # ESLint flat config (typescript-eslint + import order)
├── src/
│   ├── main.tsx                # Bootstraps StrictMode + BrowserRouter + <App />
│   ├── App.tsx                 # Root shell: Navbar + lazy-loaded routes
│   ├── style.css               # Tailwind layers + global CSS
│   ├── components/             # Reusable UI (Navbar, BooksShell, SubmitButton, Image, Avatar)
│   ├── pages/
│   │   ├── home/               # HomePage (`/`)
│   │   ├── login/              # Login (`/login`)
│   │   └── books/
│   │       ├── BooksPage.tsx           # Book grid (`/book`)
│   │       ├── sinlgeBookPage/         # Preview (`/book/:bookId`)
│   │       └── readBookPage/           # Reader (`/book/:bookId/read`)
│   ├── services/
│   │   └── apiClient/          # Axios base + auth, user, book, page clients
│   └── store/
│       └── main/               # Zustand session/loading store
└── package.json
```

---

## Major modules

### Application shell (`src/App.tsx`)

Top-level Material UI `Box` wrapping a persistent `Navbar` and the active
route outlet. Page components (`HomePage`, `Login`, `BooksPage`,
`SinlgeBookPage`, `ReadBookPage`) load on demand via `React.lazy()` so each
route ships as its own code-split chunk.

Route shape:

- `/` — home
- `/login` — auth UI
- `/book` — book grid
- `/book/:bookId` — book preview / detail
- `/book/:bookId/read` — paginated reader

### `apiClientInstance` (`src/services/apiClient/base.ts`)

Singleton Axios instance pre-configured with `baseURL = VITE_API_HOST` and
JSON content type. A request interceptor reads the `accessToken` cookie:
when present it sets `Authorization: Bearer <token>`, when missing it
redirects to `/login?redirectTo=<current path>` and aborts the request.

### `useApiClientWrapper` (`src/services/apiClient/base.ts`)

Hook returning a `wrapper` helper that toggles the global `isLoading` flag in
`useMainStore` for the duration of an awaited call. Errors are logged and
rethrown so callers can still handle them locally.

### API clients (`src/services/apiClient/{auth,user,book,page}`)

Factory hooks (`useAuthAPIClient`, `useUserAPIClient`, `useBookAPIClient`,
`usePageAPIClient`) returning a small object of typed methods that target the
backend's `/api/v1/...` routes. List endpoints accept the same
`limit/offset/sortBy/sortOrder/filters` parameters the backend exposes, and
serialize `filters` as a JSON string the way the backend's `Filter` DSL
expects.

### `useMainStore` (`src/store/main/mainStore.ts`)

Zustand store for app-wide session state: the signed-in `user` and a shared
`isLoading` flag, plus setters. Wrapped with Redux DevTools middleware.

### Components (`src/components`)

Reusable building blocks: `Navbar` (with `Logout`), `BooksShell` (layout for
book grids), `SubmitButton`, `Image`, `Avatar`. Each component lives in its
own folder with an `index.ts` barrel.

---

## Configuration

Configuration is provided to the bundle via Vite environment variables.
Variables prefixed with `VITE_` are inlined at build time and read through
`import.meta.env`.

| Variable        | Purpose                                                                                                                |
| --------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `VITE_API_HOST` | Origin used as the Axios `baseURL` for API calls. Leave empty when the backend serves the bundle from the same origin. |

`application-version.json` is read by `vite.config.ts` and exposed in code as
`import.meta.env.VITE_APP_VERSION`. Bump this file (or rely on
`package.json`'s `version`) when cutting a release.

Path aliases configured in both `vite.config.ts` and `tsconfig.app.json`:

| Alias         | Resolves to      |
| ------------- | ---------------- |
| `@components` | `src/components` |
| `@pages`      | `src/pages`      |
| `@store`      | `src/store`      |
| `@services`   | `src/services`   |

---

## Getting started

Prerequisites: Node.js 20+ and npm.

```bash
# from frontend/
npm install
npm run dev                                  # http://localhost:5173
```

Point the dev server at a running backend by exporting `VITE_API_HOST` (e.g.
`http://localhost:8000`) before `npm run dev`, or by creating a `.env.local`
file:

```dotenv
VITE_API_HOST=http://localhost:8000
```

Sign in via `/login` — the auth client posts to `/api/v1/user/login` and
stores the returned bearer token in the `accessToken` cookie. Subsequent API
calls go through `apiClientInstance` which attaches the token automatically.

---

## Available scripts

```bash
npm run dev           # Vite dev server with HMR
npm run build         # Type-check (tsc -b) then production build → ../backend/static
npm run build:watch   # Rebuild on change (same output target)
npm run preview       # Serve the production build locally
npm run lint:check    # ESLint
npm run lint:fix      # ESLint with --fix
npm run format:check  # Prettier --check
npm run format:fix    # Prettier --write
```

`npm run build` writes the bundle into `../backend/static` with hashed file
names under `assets/`, so the backend's optional `/assets` mount can serve it
directly without an extra copy step.

---

## Conventions

- **Imports** are ordered by ESLint's `import/order` rule: external packages,
  then internal aliases (`@components`, `@pages`, `@store`, `@services`),
  then relative imports, then type-only imports. A blank line separates each
  group and entries within a group are alphabetised.
- **Type imports** must use `import type { ... }` (`verbatimModuleSyntax` is
  enabled in `tsconfig.app.json`).
- **Pages and components** live in folders with a `Component.tsx`,
  a `types.ts` (when needed), and an `index.ts` barrel. Always import from
  the barrel — never reach into a sibling folder's internals.
- **Tailwind + MUI**: Tailwind's `preflight` is disabled to avoid clashing
  with MUI/Emotion's own normalisation. Prefer MUI primitives for layout and
  interactive elements; use Tailwind utility classes for spacing,
  typography, and one-off tweaks.
- **API request/response shape** mirrors the backend: camelCase keys in
  responses, `data` + `metadata` envelope for list endpoints, JSON-encoded
  `filters` query parameter for column filtering.

---

## Building for production

```bash
npm run build         # → ../backend/static/index.html + ../backend/static/assets/*
```

The backend's FastAPI factory mounts `/assets` (and `/images`) when those
directories exist, so once the bundle is built the backend will serve the
SPA in place. Bump `application-version.json` and `package.json#version`
together when releasing.
