/**
 * Zustand store for app-wide session state: the signed-in `user` and a shared `isLoading` flag.
 *
 * Wrapped with Redux DevTools middleware for debugging.
 */
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { MainStoreStateType } from './types';

/** Hook returning main store state and actions (see {@link MainStoreStateType}). */
export const useMainStore = create<MainStoreStateType>()(
  devtools((set) => ({
    isLoading: false,
    user: null,
    setIsLoading: (isLoading) => set({ isLoading }, undefined, 'setIsLoading'),
    setUser: (user) => set({ user }, undefined, 'setUser'),
  }))
);
