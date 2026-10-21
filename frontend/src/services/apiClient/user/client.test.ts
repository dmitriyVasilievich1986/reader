/**
 * Tests for {@link useUserAPIClient}: current user lookup and profile updates synced to the store.
 */

import { renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from '@store/main';

import { apiClientInstance } from '../base';
import { useUserAPIClient } from './client';

import type { UserType } from '@store/main/types';

const user: UserType = {
  id: 1,
  username: 'reader',
  email: 'reader@example.com',
  firstName: 'Leo',
  lastName: 'Tolstoy',
  photoUrl: null,
  isActive: true,
};

describe('useUserAPIClient', () => {
  beforeEach(() => {
    useMainStore.setState({ user: null, isLoading: false });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches the current user without touching the store', async () => {
    const get = vi.spyOn(apiClientInstance, 'get').mockResolvedValue({ data: user });
    const { result } = renderHook(() => useUserAPIClient());

    await expect(result.current.getUser()).resolves.toEqual(user);

    expect(get).toHaveBeenCalledWith('/api/v1/user/me');
    expect(useMainStore.getState().user).toBeNull();
  });

  it('patches the profile and stores the updated user', async () => {
    const updated = { ...user, firstName: 'Lev' };
    const patch = vi.spyOn(apiClientInstance, 'patch').mockResolvedValue({ data: updated });
    const { result } = renderHook(() => useUserAPIClient());
    const request = { firstName: 'Lev', lastName: 'Tolstoy', photoUrl: null };

    await expect(result.current.patchUser(request)).resolves.toEqual(updated);

    expect(patch).toHaveBeenCalledWith('/api/v1/user/me', request);
    expect(useMainStore.getState().user).toEqual(updated);
  });

  it('sets the loading flag while patching', async () => {
    let resolvePatch: (value: unknown) => void = () => {};
    vi.spyOn(apiClientInstance, 'patch').mockReturnValue(
      new Promise((resolve) => (resolvePatch = resolve))
    );
    const { result } = renderHook(() => useUserAPIClient());

    const promise = result.current.patchUser({ firstName: 'Lev' });
    expect(useMainStore.getState().isLoading).toBe(true);

    resolvePatch({ data: user });
    await promise;
    expect(useMainStore.getState().isLoading).toBe(false);
  });

  it('keeps the stored user and rethrows when the patch fails', async () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    useMainStore.setState({ user });
    const error = new Error('Network error');
    vi.spyOn(apiClientInstance, 'patch').mockRejectedValue(error);
    const { result } = renderHook(() => useUserAPIClient());

    await expect(result.current.patchUser({ firstName: 'Lev' })).rejects.toBe(error);

    expect(useMainStore.getState().user).toEqual(user);
    expect(useMainStore.getState().isLoading).toBe(false);
  });
});
