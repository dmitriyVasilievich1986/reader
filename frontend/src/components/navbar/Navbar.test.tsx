/**
 * Tests for {@link Navbar}: logo, home link and the user menu shown only when signed in.
 */

import { render, screen } from '@testing-library/react';
import Cookies from 'js-cookie';
import { MemoryRouter } from 'react-router';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main';

import { Navbar } from './Navbar';

const { getUser } = vi.hoisted(() => ({ getUser: vi.fn() }));

vi.mock('@services/apiClient/user', () => ({
  useUserAPIClient: () => ({ getUser }),
}));

function renderNavbar() {
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>
  );
}

describe('Navbar', () => {
  beforeEach(() => {
    useMainStore.setState({ user: null, isLoading: false });
    getUser.mockReturnValue(new Promise(() => {}));
  });

  afterEach(() => {
    Cookies.remove('accessToken');
  });

  it('renders the logo and a link home', () => {
    renderNavbar();

    expect(screen.getByRole('img', { name: 'Home' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Home' })).toHaveAttribute('href', '/');
  });

  it('hides the user menu when signed out', () => {
    renderNavbar();

    expect(screen.queryByText('Logout')).not.toBeInTheDocument();
  });

  it('shows the user menu when signed in', () => {
    Cookies.set('accessToken', 'token-123');
    renderNavbar();

    expect(screen.getByText('Logout')).toBeInTheDocument();
  });
});
