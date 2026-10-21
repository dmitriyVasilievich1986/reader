# AGENTS.md — Frontend

Guidance for AI coding agents working inside `frontend/`. This file covers the
frontend only; project-level architecture (backend, Docker, nginx, CI) is
described elsewhere.

## Stack

- TypeScript 5.6 (`strict`), React 18 (StrictMode)
- Toolchain: [Vite+](https://viteplus.dev) 1.3 (`vite-plus`, CLI `vp`) — Vite
  (`vite` is aliased to `@voidzero-dev/vite-plus-core` via `overrides`),
  Oxlint for linting, Oxfmt for formatting. All configured in `vite.config.ts`.
- Routing: `react-router` v7 (`BrowserRouter`, `Routes`, `useSearchParams`, `useNavigate`)
- UI: MUI v9 (`@mui/material`, `@mui/icons-material`) + Emotion
- Styling: Tailwind CSS 3 (Preflight **disabled**), CSS Modules (`style.module.css`)
- State: Zustand 5 with `devtools` middleware
- HTTP: Axios + `js-cookie` (bearer token in the `accessToken` cookie)
- Utilities: `dayjs`, `classnames`, `rison`

There is no test runner configured. Verify changes with type-check, lint and
format (see below).

## Commands

Run from `frontend/`. The npm scripts wrap `vp`; `npx vp <command>` works too
(`npx vp help` lists everything).

```bash
npm run dev           # vp dev — dev server (http://localhost:5173)
npm run build         # tsc -b && vp build → dist/
npm run build:watch   # vp build --watch
npm run preview       # vp preview — serve dist/
npm run lint:check    # vp lint .
npm run lint:fix      # vp lint . --fix
npm run format:check  # vp fmt --check .
npm run format:fix    # vp fmt .
npx vp check          # format + lint + type check in one run
```

Before finishing a change, all of these must pass (no errors; don't add new
warnings):

```bash
npx tsc -b && npx vp check
```

Do not run `npm run build` just to verify — it writes into `dist/`.

## Source layout

```
src/
├── main.tsx          # StrictMode + BrowserRouter + <App />
├── App.tsx           # Navbar + lazy-loaded <Routes>
├── style.css         # Tailwind layers + global CSS
├── vite-env.d.ts     # Typed import.meta.env
├── assets/           # SVGs
├── components/       # Reusable UI (navbar, booksShell, image, avatar, search, submitButton)
├── pages/            # Route-level components (home, login, books, authors, profile)
├── services/apiClient/  # Axios instance + per-resource clients (auth, user, book, author, page)
├── store/main/       # Zustand store: user + isLoading
└── utils/            # Pure helpers (parseIntWithCheck, getAuthorName)
```

### Path aliases

Defined in **both** `vite.config.ts` (`resolve.alias`) and `tsconfig.app.json`
(`paths`). Keep them in sync when adding one.

| Alias         | Path             |
| ------------- | ---------------- |
| `@components` | `src/components` |
| `@pages`      | `src/pages`      |
| `@store`      | `src/store`      |
| `@services`   | `src/services`   |
| `@utils`      | `src/utils`      |
| `@assets`     | `src/assets`     |

## Conventions

### Folder / module structure

- Each component or page lives in its own camelCase folder with:
  - `ComponentName.tsx` (PascalCase, named export — no default exports except `App.tsx`)
  - `types.ts` when it has props/types of its own
  - `style.module.css` when it needs CSS Modules
  - `index.ts` barrel re-exporting the public API
- Register new components in `src/components/index.ts` and new pages in
  `src/pages/index.tsx`.
- Import other modules through their barrel / alias (`@components/booksShell`),
  not through deep relative paths into another folder.

### Routing

- Routes are declared in `src/App.tsx`. Pages are loaded with `React.lazy()`
  inside a `Suspense` fallback:
  ```tsx
  const BooksPage = lazy(() => import('@pages/books').then((m) => ({ default: m.BooksPage })));
  ```
- Keep URL state (pagination, filters) in search params via `useSearchParams`.

### API clients

- All HTTP goes through `apiClientInstance` in `src/services/apiClient/base.ts`.
  It sets `baseURL` from `VITE_API_HOST`, attaches `Authorization: Bearer <token>`
  and redirects to `/login?redirectTo=...` when the cookie is missing or the API
  returns 401. Do not create other Axios instances or call `fetch` directly.
- One folder per resource: `apiClient/<resource>/{client.ts,types.ts,index.ts}`.
- A client is a `use<Resource>APIClient` hook returning an object of typed async
  methods that target `/api/v1/<resource>...` and return `response.data`.
- List endpoints take `limit, offset, sortBy, sortOrder, filters?: FilterType[]`;
  `filters` is sent as `JSON.stringify(filters)`. Responses use the
  `{ data, metadata: PaginationMetadata }` envelope (see `apiClient/types.ts`).
- Wrap calls with `useApiClientWrapper().wrapper(...)` when they should drive the
  global `isLoading` flag.
- Response/request types use camelCase field names, mirroring the backend.

### State

- Global state lives in Zustand (`src/store`). Add new state to an existing slice
  or a new folder under `src/store/<slice>/` with `types.ts` + `<slice>Store.ts`,
  wrapped in `devtools`, and name each action in `set(..., undefined, 'actionName')`.
- Select only what you need: `useMainStore((state) => state.setIsLoading)`.
- Component-local state stays in `useState`.

### Styling

- Prefer MUI components for layout and interactive elements; import them by
  path (`import Box from '@mui/material/Box'`), not from the package root.
- Use the MUI `sx` prop for component-specific styles, Tailwind utilities for
  spacing/typography tweaks, and CSS Modules for complex component CSS.
- Tailwind `preflight` is disabled on purpose (MUI owns base styles). Do not
  enable it. Use theme colors `reader-teal`, `reader-cream`, `reader-muted`
  (also available as `theme('colors.reader.*')` in CSS).
- Use `classnames` to compose conditional class names.

### Environment variables

- Only `VITE_`-prefixed variables are exposed, via `import.meta.env`.
- Declare every new variable in `src/vite-env.d.ts` (`ImportMetaEnv`).
- `VITE_APP_VERSION` is injected from `application-version.json` by `vite.config.ts`.

### Documentation

- Every file starts with a JSDoc module comment; exported functions, components
  and types get JSDoc (`@param`, `@returns`, `@property`). Follow
  `../.cursor/rules/js_add_docstring.mdc`. Match the existing comment density.

## TypeScript rules (`tsconfig.app.json`)

- `strict`, `noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`,
  `noUncheckedSideEffectImports`.
- `verbatimModuleSyntax`: type-only imports **must** use `import type { X }` or
  inline `type` (`import { useBookAPIClient, type BookType } from '...'`).
- Prefer `type` aliases over `interface` (existing code uses `type`); suffix
  data shapes with `Type` (`BookType`, `UserType`) and props with `Props`.
- Avoid `any`; type Axios calls with generics (`apiClientInstance.get<BookType>(...)`).

## Lint rules (Oxlint, `lint` block in `vite.config.ts`)

Generated by `vp migrate` from the former ESLint config; `dist` and
`node_modules` are ignored. Edit the `lint` block, not a separate config file.

- Plugins `oxc`, `typescript`, `unicorn`; the `correctness` category is `warn`.
- `options.typeAware` / `options.typeCheck` are on: lint runs type-aware rules
  (e.g. `typescript/no-floating-promises`) and reports type errors. Mark
  intentionally un-awaited promises with `void`.
- `**/*.{ts,tsx}` override: the former `@eslint/js` + `typescript-eslint`
  recommended rules (e.g. `typescript/no-explicit-any`, `prefer-const`) plus:
  - `react/*` (React Compiler / hooks rules) on, **except**
    `react/exhaustive-deps`, which is `off`. Still list dependencies deliberately.
  - `react/only-export-components`: `warn` (`allowConstantExport: true`) —
    files exporting components should export only components (plus constants).
  - `no-unused-vars`: `error`; prefix intentionally unused args/vars/caught
    errors with `_` (e.g. `(_, value) => ...`).
  - `import/no-duplicates`: `error` — merge imports from the same module.
  - `import/newline-after-import`: `error` — exactly one blank line after imports.
- `vite-plus/prefer-vite-plus-imports`: `error` — import Vite APIs from
  `vite-plus` (e.g. `defineConfig`), not `vite`.

### Import order

Oxlint has no `import/order`, so import order is **no longer enforced
automatically**. Keep the existing convention by hand — blank lines between
groups, alphabetical (case-insensitive) within each:

1. builtin + external packages (`react`, `@mui/...`, `react-router`, `zustand`)
2. internal aliases (`@components/...`, `@store/...`, `@utils/...`, `@services/...`)
3. parent / sibling / index (`../x`, `./x`)
4. type imports (`import type ...`)

Example:

```ts
import Container from '@mui/material/Container';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router';

import { BooksShell } from '@components/booksShell';
import { useBookAPIClient } from '@services/apiClient/book';

import styles from './style.module.css';

import type { BookType } from '@services/apiClient/book';
```

## Format rules (Oxfmt, `fmt` block in `vite.config.ts`)

Prettier-compatible options carried over from the old `.prettierrc`:

```ts
fmt: {
  semi: true,
  singleQuote: true,
  trailingComma: 'es5',
  printWidth: 100,
  tabWidth: 2,
  arrowParens: 'always',
  sortPackageJson: false,
}
```

- Semicolons always; single quotes in TS (JSX attributes keep double quotes).
- Trailing commas where valid in ES5 (objects, arrays) — not in function params.
- Max line width 100, 2-space indentation.
- Always parenthesize arrow function params: `(x) => x`.
- `package.json` keys are not re-sorted.
- Oxfmt runs on the whole `frontend/` folder. Run `npm run format:fix` after
  editing; do not hand-format against it.

## Don'ts

- Don't add ESLint, Prettier or their config files back; lint and format
  config live in `vite.config.ts`.
- Don't remove the `vite` → `@voidzero-dev/vite-plus-core` alias/override in
  `package.json`; Vite+ relies on it.
- Don't edit `dist/` or `node_modules/` by hand.
- Don't add a second HTTP client, router or state library.
- Don't commit secrets to `.env`; it only holds the local `VITE_API_HOST`.
- Don't add dependencies without need; if you do, use `npm install` so
  `package-lock.json` stays in sync.
