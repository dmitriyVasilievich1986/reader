/**
 * Tests for the {@link Login} page: form input, password visibility, submit, cookie, redirect and errors.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router';
import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main/mainStore';

import { Login } from './Login';

const { login, setCookie } = vi.hoisted(() => ({ login: vi.fn(), setCookie: vi.fn() }));

vi.mock('@services/apiClient/auth', () => ({
  useAuthAPIClient: () => ({ login }),
}));

vi.mock('js-cookie', () => ({
  default: { set: setCookie },
}));

const loginResponse = {
  accessToken: 'token-123',
  expiresAt: '2030-01-01T00:00:00Z',
};

function LocationDisplay() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname + location.search}</div>;
}

function renderLogin(initialEntry = '/login') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<LocationDisplay />} />
      </Routes>
    </MemoryRouter>
  );
}

describe('Login', () => {
  beforeEach(() => {
    useMainStore.setState({ user: null, isLoading: false });
    login.mockResolvedValue(loginResponse);
  });

  it('renders username and masked password fields', () => {
    renderLogin();

    expect(screen.getByLabelText('Username')).toHaveAttribute('type', 'text');
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button', { name: 'Login' })).toBeEnabled();
  });

  it('toggles password visibility', async () => {
    const user = userEvent.setup();
    renderLogin();
    const toggle = screen.getByRole('button', { name: 'Toggle password visibility' });

    await user.click(toggle);
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'text');

    await user.click(toggle);
    expect(screen.getByLabelText('Password')).toHaveAttribute('type', 'password');
  });

  it('logs in, stores the token cookie and navigates home by default', async () => {
    const user = userEvent.setup();
    renderLogin();

    await user.type(screen.getByLabelText('Username'), 'reader');
    await user.type(screen.getByLabelText('Password'), 'secret');
    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(await screen.findByTestId('location')).toHaveTextContent(/^\/$/);
    expect(login).toHaveBeenCalledWith('reader', 'secret');
    expect(setCookie).toHaveBeenCalledWith('accessToken', 'token-123', {
      expires: new Date(loginResponse.expiresAt),
    });
  });

  it('submits on Enter and navigates to redirectTo', async () => {
    const user = userEvent.setup();
    renderLogin('/login?redirectTo=/book');

    await user.type(screen.getByLabelText('Username'), 'reader');
    await user.type(screen.getByLabelText('Password'), 'secret{Enter}');

    expect(await screen.findByTestId('location')).toHaveTextContent('/book');
    expect(login).toHaveBeenCalledWith('reader', 'secret');
  });

  it('shows the API error on both fields and clears it on input', async () => {
    const user = userEvent.setup();
    login.mockRejectedValue({ response: { data: { detail: 'Invalid credentials' } } });
    renderLogin();

    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(await screen.findAllByText('Invalid credentials')).toHaveLength(2);
    expect(screen.getByLabelText('Username')).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByLabelText('Password')).toHaveAttribute('aria-invalid', 'true');
    expect(setCookie).not.toHaveBeenCalled();
    expect(screen.queryByTestId('location')).not.toBeInTheDocument();

    await user.type(screen.getByLabelText('Username'), 'a');
    expect(screen.queryByText('Invalid credentials')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toHaveAttribute('aria-invalid', 'false');
  });

  it('shows a fallback message when the error has no detail', async () => {
    const user = userEvent.setup();
    login.mockRejectedValue(new Error('Network Error'));
    renderLogin();

    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(await screen.findAllByText('An unknown error occurred')).toHaveLength(2);
  });

  it('clears the current user from the store on mount', async () => {
    useMainStore.setState({
      user: {
        id: 1,
        username: 'reader',
        email: 'reader@example.com',
        firstName: null,
        lastName: null,
        photoUrl: null,
        isActive: true,
      },
    });
    renderLogin();

    await waitFor(() => {
      expect(useMainStore.getState().user).toBeNull();
    });
  });
});
