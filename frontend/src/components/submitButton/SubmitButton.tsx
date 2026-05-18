/**
 * Contained submit-style button that reflects global loading state from the main store.
 */

import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';

import { useMainStore } from '@store/main';

/**
 * Renders a Material UI contained `Button`; while `useMainStore().isLoading` is true, the label is
 * replaced by a small indeterminate `CircularProgress`.
 *
 * @param {object} props - Component props.
 * @param {boolean | undefined} props.disabled - When true, the button is not interactive.
 * @param {string} props.label - Visible text when the app is not in a loading state.
 * @param {'primary' | 'secondary' | 'error'} props.color - MUI button color theme.
 * @param {(event: React.MouseEvent<HTMLButtonElement>) => void | undefined} props.onClick - Click handler.
 * @returns {JSX.Element} Contained button or spinner.
 */
export function SubmitButton(props: {
  disabled?: boolean;
  label: string;
  color: 'primary' | 'secondary' | 'error';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}) {
  const isLoading = useMainStore((state) => state.isLoading);

  return (
    <Button
      variant="contained"
      color={props.color}
      disabled={props.disabled || isLoading}
      onClick={props.onClick}
    >
      {isLoading ? <CircularProgress size={20} /> : props.label}
    </Button>
  );
}
