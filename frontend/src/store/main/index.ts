/**
 * Barrel module for the main Zustand store: re-exports {@link useMainStore} and public entity types from `./types`.
 */

import { useMainStore } from './mainStore';

import type { MainStoreStateType } from './types';

export { useMainStore, type MainStoreStateType };
