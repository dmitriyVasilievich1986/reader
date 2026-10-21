/**
 * Tests for {@link useAuthAPIClient}: login request shape, response and loading state.
 */

import { renderHook } from '@testing-library/react';
import axios from 'axios';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main';

import { useAuthAPIClient } from './client';

const loginResponse = { accessToken: 'token-123', expiresAt: '2030-01-01T00:00:00Z' };

describe('useAuthAPIClient', () => {
  beforeEach(() => {
    useMainStore.setState({ isLoading: false });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('posts the credentials to the login endpoint and returns the token', async () => {
    const post = vi.spyOn(axios, 'post').mockResolvedValue({ data: loginResponse });
    const { result } = renderHook(() => useAuthAPIClient());

    await expect(result.current.login('reader', 'secret')).resolves.toEqual(loginResponse);

    expect(post).toHaveBeenCalledWith(
      `${import.meta.env.VITE_API_HOST ?? ''}/api/v1/user/login`,
      { username: 'reader', password: 'secret' },
      { headers: { 'Content-Type': 'application/json' } }
    );
  });

  it('sets the loading flag while logging in', async () => {
    let resolvePost: (value: unknown) => void = () => {};
    vi.spyOn(axios, 'post').mockReturnValue(new Promise((resolve) => (resolvePost = resolve)));
    const { result } = renderHook(() => useAuthAPIClient());

    const promise = result.current.login('reader', 'secret');
    expect(useMainStore.getState().isLoading).toBe(true);

    resolvePost({ data: loginResponse });
    await promise;
    expect(useMainStore.getState().isLoading).toBe(false);
  });

  it('rethrows login errors', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const error = new Error('Invalid credentials');
    vi.spyOn(axios, 'post').mockRejectedValue(error);
    const { result } = renderHook(() => useAuthAPIClient());

    await expect(result.current.login('reader', 'wrong')).rejects.toBe(error);
    expect(useMainStore.getState().isLoading).toBe(false);
  });
});
