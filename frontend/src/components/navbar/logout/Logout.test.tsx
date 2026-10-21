/**
 * Tests for {@link Logout}: loading the signed-in user, the user label and avatar, menu navigation
 * and logging out.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Cookies from 'js-cookie';
import { MemoryRouter, useLocation } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main';

import { Logout } from './Logout';

import type { UserType } from '@store/main/types';

const { getUser } = vi.hoisted(() => ({ getUser: vi.fn() }));

vi.mock('@services/apiClient/user', () => ({
  useUserAPIClient: () => ({ getUser }),
}));

const user: UserType = {
  id: 1,
  username: 'reader',
  email: 'reader@example.com',
  firstName: 'Leo',
  lastName: 'Tolstoy',
  photoUrl: null,
  isActive: true,
};

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}</div>;
}

function renderLogout() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Logout />
      <LocationDisplay />
    </MemoryRouter>
  );
}

/** Opens the user menu by clicking the trigger showing `label`. */
const openMenu = async (label: string) => {
  const actions = userEvent.setup();
  await actions.click(await screen.findByText(label));
  return actions;
};

describe('Logout', () => {
  beforeEach(() => {
    useMainStore.setState({ user: null, isLoading: false });
    Cookies.set('accessToken', 'token-123');
    getUser.mockResolvedValue(user);
  });

  afterEach(() => {
    Cookies.remove('accessToken');
  });

  it('renders nothing and skips loading the user when signed out', () => {
    Cookies.remove('accessToken');
    const { container } = renderLogout();

    expect(container).toHaveTextContent(/^\/$/);
    expect(getUser).not.toHaveBeenCalled();
  });

  it('shows a Logout label until the user is loaded', () => {
    getUser.mockReturnValue(new Promise(() => {}));
    renderLogout();

    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.queryByLabelText('avatar')).not.toBeInTheDocument();
  });

  it('loads the user into the store and shows their name and initials', async () => {
    renderLogout();

    expect(await screen.findByText('Leo Tolstoy')).toBeInTheDocument();
    expect(screen.getByLabelText('avatar')).toHaveTextContent('LT');
    expect(useMainStore.getState().user).toEqual(user);
  });

  it('falls back to the username without a full name', async () => {
    getUser.mockResolvedValue({ ...user, lastName: null });
    renderLogout();

    expect(await screen.findByText('reader')).toBeInTheDocument();
    expect(screen.getByLabelText('avatar')).toHaveTextContent('RE');
  });

  it('does not refetch a user that is already in the store', () => {
    useMainStore.setState({ user });
    renderLogout();

    expect(getUser).not.toHaveBeenCalled();
    expect(screen.getByText('Leo Tolstoy')).toBeInTheDocument();
  });

  it('opens a menu with the navigation items and app version', async () => {
    renderLogout();
    await openMenu('Leo Tolstoy');

    const items = screen.getAllByRole('menuitem').map((item) => item.textContent);
    expect(items).toEqual([
      'Profile',
      'Books',
      'Authors',
      'Logout',
      expect.stringMatching(/^Version /),
    ]);
  });

  it.each([
    ['Profile', '/profile'],
    ['Books', '/book'],
    ['Authors', '/author'],
  ])('navigates to %s and closes the menu', async (label, path) => {
    renderLogout();
    const actions = await openMenu('Leo Tolstoy');

    await actions.click(screen.getByRole('menuitem', { name: label }));

    expect(screen.getByTestId('location')).toHaveTextContent(path);
    await waitFor(() => {
      expect(screen.queryByRole('menu')).not.toBeInTheDocument();
    });
  });

  it('removes the token and navigates to login on logout', async () => {
    renderLogout();
    const actions = await openMenu('Leo Tolstoy');

    await actions.click(screen.getByRole('menuitem', { name: 'Logout' }));

    expect(Cookies.get('accessToken')).toBeUndefined();
    expect(screen.getByTestId('location')).toHaveTextContent('/login');
  });
});
