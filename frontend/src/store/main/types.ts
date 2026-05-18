/**
 * Zustand main slice types: authenticated user payload and combined store state shape.
 */

/**
 * User record returned by the backend (mirrors `/api/v1/user` styles).
 *
 * @property {number} id - User primary key.
 * @property {string} username - Login handle.
 * @property {string} email - Contact email.
 * @property {(string | null)} firstName - Given name when provided.
 * @property {(string | null)} lastName - Family name when provided.
 * @property {(string | null)} photoUrl - Avatar URL, or null when unset.
 * @property {boolean} isActive - Whether the account is enabled.
 */
export type UserType = {
  id: number;
  username: string;
  email: string;
  firstName: string | null;
  lastName: string | null;
  photoUrl: string | null;
  isActive: boolean;
};

/**
 * State and actions exposed by the main Zustand store.
 *
 * @property {boolean} isLoading - Shared busy flag for bootstrap or global fetches.
 * @property {(UserType | null)} user - Current session user, or null when signed out / not loaded.
 * @property {(isLoading: boolean) => void} setIsLoading - Updates `isLoading`.
 * @property {(user: UserType | null) => void} setUser - Replaces or clears `user`.
 */
export type MainStoreStateType = {
  isLoading: boolean;
  user: UserType | null;
  setIsLoading: (isLoading: boolean) => void;
  setUser: (user: UserType | null) => void;
};
