/**
 * Tests for the {@link Profile} page: loading skeleton and the profile form once the user is loaded.
 */

import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main/mainStore';

import { Profile } from './Profile';

import type { UserType } from '@store/main/types';

vi.mock('@services/apiClient/user', () => ({
  useUserAPIClient: () => ({ patchUser: vi.fn() }),
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

describe('Profile', () => {
  beforeEach(() => {
    useMainStore.setState({ user: null, isLoading: false });
  });

  it('shows a skeleton while there is no user', () => {
    render(<Profile />);

    expect(screen.queryByRole('heading', { name: 'Profile' })).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  it('shows a skeleton while loading even when a user is set', () => {
    useMainStore.setState({ user, isLoading: true });
    render(<Profile />);

    expect(screen.queryByRole('heading', { name: 'Profile' })).not.toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  it('renders the profile form for the loaded user', () => {
    useMainStore.setState({ user });
    render(<Profile />);

    expect(screen.getByRole('heading', { name: 'Profile' })).toBeInTheDocument();
    expect(screen.getByLabelText('First name')).toHaveValue('Leo');
  });
});
