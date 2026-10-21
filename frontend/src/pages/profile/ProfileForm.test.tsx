/**
 * Tests for {@link ProfileForm}: prefilled values, unsaved-change highlighting and saving via the user API.
 */

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main/mainStore';

import { ProfileForm } from './ProfileForm';

import type { UserType } from '@store/main/types';

const { patchUser } = vi.hoisted(() => ({ patchUser: vi.fn() }));

vi.mock('@services/apiClient/user', () => ({
  useUserAPIClient: () => ({ patchUser }),
}));

const user: UserType = {
  id: 1,
  username: 'reader',
  email: 'reader@example.com',
  firstName: 'Leo',
  lastName: 'Tolstoy',
  photoUrl: 'https://example.com/leo.png',
  isActive: true,
};

/** Returns the MUI input root wrapping the field with the given label. */
const inputRoot = (label: string) => screen.getByLabelText(label).closest('.MuiInputBase-root');

describe('ProfileForm', () => {
  beforeEach(() => {
    useMainStore.setState({ user, isLoading: false });
    patchUser.mockResolvedValue(user);
  });

  it('prefills the fields from the store user', () => {
    render(<ProfileForm />);

    expect(screen.getByLabelText('First name')).toHaveValue('Leo');
    expect(screen.getByLabelText('Last name')).toHaveValue('Tolstoy');
    expect(screen.getByLabelText('Photo URL')).toHaveValue('https://example.com/leo.png');
  });

  it('renders empty fields for null user values', () => {
    useMainStore.setState({ user: { ...user, firstName: null, lastName: null, photoUrl: null } });
    render(<ProfileForm />);

    expect(screen.getByLabelText('First name')).toHaveValue('');
    expect(screen.getByLabelText('Last name')).toHaveValue('');
    expect(screen.getByLabelText('Photo URL')).toHaveValue('');
  });

  it('highlights only the fields with unsaved changes', async () => {
    const userActions = userEvent.setup();
    render(<ProfileForm />);

    expect(inputRoot('First name')).not.toHaveClass('MuiInputBase-colorWarning');

    await userActions.type(screen.getByLabelText('First name'), 'nid');

    expect(inputRoot('First name')).toHaveClass('MuiInputBase-colorWarning');
    expect(inputRoot('Last name')).not.toHaveClass('MuiInputBase-colorWarning');
    expect(inputRoot('Photo URL')).not.toHaveClass('MuiInputBase-colorWarning');
  });

  it('saves the edited values', async () => {
    const userActions = userEvent.setup();
    render(<ProfileForm />);

    await userActions.clear(screen.getByLabelText('First name'));
    await userActions.type(screen.getByLabelText('First name'), 'Lev');
    await userActions.clear(screen.getByLabelText('Photo URL'));
    await userActions.click(screen.getByRole('button', { name: 'Save' }));

    expect(patchUser).toHaveBeenCalledOnce();
    expect(patchUser).toHaveBeenCalledWith({
      firstName: 'Lev',
      lastName: 'Tolstoy',
      photoUrl: '',
    });
  });

  it('disables saving while a request is in progress', () => {
    useMainStore.setState({ isLoading: true });
    render(<ProfileForm />);

    expect(screen.getByRole('button')).toBeDisabled();
  });
});
