/**
 * Search field that persists the query string in the URL via React Router `useSearchParams`.
 */
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import { useState } from 'react';
import { useSearchParams } from 'react-router';

/**
 * Outlined text input with a search icon. Typing updates local state; pressing Enter or clicking the
 * icon writes the value to the named query parameter (or removes it when empty).
 *
 * @param {object} props - Component props.
 * @param {string} props.label - MUI TextField label.
 * @param {string} [props.paramName] - URL query key for the search term; defaults to `"search"`.
 * @returns {JSX.Element} Text field with start adornment and URL sync on commit.
 */
export function Search(props: { label: string; paramName?: string }) {
  const paramName = props.paramName ?? 'search';
  const [searchParams, setSearchParams] = useSearchParams();

  const [search, setSearch] = useState<string>(searchParams.get(paramName) ?? '');

  /**
   * Updates URL search params: sets `paramName` when `value` is non-empty, otherwise deletes it.
   *
   * @param {string} value - Text to store under the configured query parameter.
   */
  const searchHandler = (value: string) => {
    setSearchParams((previous) => {
      if (value.length > 0) {
        previous.set(paramName, value);
      } else {
        previous.delete(paramName);
      }
      previous.set('page', '0');
      return previous;
    });
  };

  return (
    <TextField
      sx={{ width: '300px' }}
      label={props.label}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon onClick={() => searchHandler(search)} sx={{ cursor: 'pointer' }} />
            </InputAdornment>
          ),
        },
      }}
      variant="outlined"
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') searchHandler(search);
      }}
    />
  );
}
