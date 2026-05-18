import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';

export default tseslint.config([
  { ignores: ['dist', 'node_modules'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [js.configs.recommended, ...tseslint.configs.recommended, prettier],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      import: importPlugin,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-hooks/exhaustive-deps': 'off',
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],
      // Import ordering rules
      'import/order': [
        'error',
        {
          groups: [
            ['builtin', 'external'], // External packages (react, gd-design-library, etc.) - no spacing between them
            'internal', // Local imports (@components, @store, @utils, @services, @hooks)
            ['parent', 'sibling', 'index'], // Relative imports (./, ../)
            'object',
            'type', // Type imports
          ],
          pathGroups: [
            // Local imports group (excluding constants)
            {
              pattern: '@{components,store,utils,services,hooks}/**',
              group: 'internal',
              position: 'before',
            },
            // Constants as separate group after local imports
            {
              pattern: '@constants',
              group: 'internal',
              position: 'after',
            },
          ],
          pathGroupsExcludedImportTypes: ['builtin'],
          'newlines-between': 'always',
          alphabetize: {
            order: 'asc',
            caseInsensitive: true,
          },
          warnOnUnassignedImports: false,
        },
      ],
      'import/newline-after-import': ['error', { count: 1 }],
      'import/no-duplicates': 'error',
    },
  },
]);
