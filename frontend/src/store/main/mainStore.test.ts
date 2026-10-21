/**
 * Tests for {@link useMainStore}: initial state and the `setIsLoading` / `setUser` actions.
 */

import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';

import { useMainStore } from './mainStore';

import type { UserType } from './types';

const initialState = useMainStore.getState();

const user: UserType = {
  id: 1,
  username: 'reader',
  email: 'reader@example.com',
  firstName: 'Leo',
  lastName: 'Tolstoy',
  photoUrl: null,
  isActive: true,
};

describe('useMainStore', () => {
  beforeEach(() => {
    useMainStore.setState(initialState, true);
  });

  it('starts signed out and not loading', () => {
    const state = useMainStore.getState();

    expect(state.user).toBeNull();
    expect(state.isLoading).toBe(false);
  });

  it('sets and clears the loading flag', () => {
    useMainStore.getState().setIsLoading(true);
    expect(useMainStore.getState().isLoading).toBe(true);

    useMainStore.getState().setIsLoading(false);
    expect(useMainStore.getState().isLoading).toBe(false);
  });

  it('sets and clears the user', () => {
    useMainStore.getState().setUser(user);
    expect(useMainStore.getState().user).toEqual(user);

    useMainStore.getState().setUser(null);
    expect(useMainStore.getState().user).toBeNull();
  });

  it('updates one field without touching the other', () => {
    useMainStore.getState().setUser(user);
    useMainStore.getState().setIsLoading(true);

    expect(useMainStore.getState()).toMatchObject({ user, isLoading: true });
  });

  it('notifies subscribers on change', () => {
    const listener = vi.fn();
    const unsubscribe = useMainStore.subscribe(listener);

    useMainStore.getState().setIsLoading(true);
    unsubscribe();
    useMainStore.getState().setIsLoading(false);

    expect(listener).toHaveBeenCalledOnce();
    expect(listener.mock.calls[0][0]).toMatchObject({ isLoading: true });
    expect(listener.mock.calls[0][1]).toMatchObject({ isLoading: false });
  });
});
