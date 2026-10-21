/**
 * Tests for {@link SubmitButton}: label, click handling and the global loading state.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main';

import { SubmitButton } from './SubmitButton';

describe('SubmitButton', () => {
  beforeEach(() => {
    useMainStore.setState({ isLoading: false });
  });

  it('renders the label with the given color', () => {
    render(<SubmitButton label="Save" color="error" />);

    const button = screen.getByRole('button', { name: 'Save' });
    expect(button).toBeEnabled();
    expect(button).toHaveClass('MuiButton-contained', 'MuiButton-colorError');
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<SubmitButton label="Save" color="primary" onClick={onClick} />);

    await user.click(screen.getByRole('button', { name: 'Save' }));

    expect(onClick).toHaveBeenCalledOnce();
  });

  it('is disabled when the disabled prop is set', async () => {
    // MUI sets `pointer-events: none` on disabled buttons; skip that check to attempt the click.
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const onClick = vi.fn();
    render(<SubmitButton label="Save" color="primary" disabled onClick={onClick} />);

    const button = screen.getByRole('button', { name: 'Save' });
    expect(button).toBeDisabled();
    await user.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it('shows a spinner and is disabled while loading', () => {
    useMainStore.setState({ isLoading: true });
    render(<SubmitButton label="Save" color="primary" />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).not.toHaveTextContent('Save');
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
